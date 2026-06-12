from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
from dotenv import load_dotenv

from models import db, User, NGO, Admin, Donation, Request
from forms import UserRegistrationForm, NGORegistrationForm, LoginForm, DonationForm
from utils import check_expired_donations, get_nearby_donations, get_donation_stats, format_time_ago, format_time_remaining

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///food_donation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Template filters
app.jinja_env.filters['time_ago'] = format_time_ago
app.jinja_env.filters['time_remaining'] = format_time_remaining


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    user_type = session.get('user_type')
    
    if user_type == 'user':
        return User.query.get(int(user_id))
    elif user_type == 'ngo':
        return NGO.query.get(int(user_id))
    elif user_type == 'admin':
        return Admin.query.get(int(user_id))
    
    return None


def role_required(role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('login'))
            
            if session.get('user_type') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    stats = get_donation_stats()
    return render_template('index.html', stats=stats)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user_form = UserRegistrationForm()
    ngo_form = NGORegistrationForm()
    
    # Handle user registration
    if request.method == 'POST' and 'user_submit' in request.form:
        if user_form.validate_on_submit():
            user = User(
                username=user_form.username.data,
                email=user_form.email.data,
                password_hash=generate_password_hash(user_form.password.data),
                phone_number=user_form.phone_number.data,
                location=user_form.location.data,
                role=user_form.role.data
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    # Handle NGO registration
    if request.method == 'POST' and 'ngo_submit' in request.form:
        if ngo_form.validate_on_submit():
            ngo = NGO(
                ngo_name=ngo_form.ngo_name.data,
                email=ngo_form.email.data,
                password_hash=generate_password_hash(ngo_form.password.data),
                phone_number=ngo_form.phone_number.data,
                location=ngo_form.location.data,
                registration_number=ngo_form.registration_number.data,
                address=ngo_form.address.data
            )
            db.session.add(ngo)
            db.session.commit()
            
            flash('NGO registration successful! Please wait for admin verification.', 'info')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html', user_form=user_form, ngo_form=ngo_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login for all user types"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data
        
        user = None
        
        if user_type == 'user':
            user = User.query.filter_by(email=email).first()
        elif user_type == 'ngo':
            user = NGO.query.filter_by(email=email).first()
            if user and not user.is_verified:
                flash('Your NGO account is pending verification by admin.', 'warning')
                return redirect(url_for('login'))
        elif user_type == 'admin':
            user = Admin.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['user_type'] = user_type
            
            flash(f'Welcome back!', 'success')
            
            # Redirect based on user type
            if user_type == 'user':
                return redirect(url_for('user_dashboard'))
            elif user_type == 'ngo':
                return redirect(url_for('ngo_dashboard'))
            elif user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout"""
    session.pop('user_type', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ==================== USER ROUTES ====================

@app.route('/user/dashboard')
@login_required
@role_required('user')
def user_dashboard():
    """User dashboard"""
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).limit(5).all()
    
    stats = {
        'total_donations': Donation.query.filter_by(donor_id=current_user.id).count(),
        'active_donations': Donation.query.filter_by(donor_id=current_user.id, status='available').count(),
        'completed': Donation.query.filter_by(donor_id=current_user.id, status='collected').count()
    }
    
    return render_template('user/dashboard.html', donations=donations, stats=stats)


@app.route('/user/donate', methods=['GET', 'POST'])
@login_required
@role_required('user')
def user_donate():
    """Add food donation"""
    form = DonationForm()
    
    if form.validate_on_submit():
        donation = Donation(
            donor_id=current_user.id,
            food_name=form.food_name.data,
            quantity=form.quantity.data,
            food_time=form.food_time.data,
            expiry_datetime=form.expiry_datetime.data,
            location=form.location.data,
            description=form.description.data
        )
        db.session.add(donation)
        db.session.commit()
        
        flash('Food donation posted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/donate.html', form=form)


@app.route('/user/available')
@login_required
@role_required('user')
def user_available():
    """View available food donations"""
    location_filter = request.args.get('location', '')
    time_filter = request.args.get('time', '')
    
    query = Donation.query.filter(
        Donation.status == 'available',
        Donation.expiry_datetime > datetime.utcnow()
    )
    
    if location_filter:
        query = query.filter(Donation.location == location_filter)
    
    if time_filter:
        query = query.filter(Donation.food_time == time_filter)
    
    donations = query.order_by(Donation.created_at.desc()).all()
    
    return render_template('user/available.html', donations=donations)


@app.route('/user/history')
@login_required
@role_required('user')
def user_history():
    """View donation history"""
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    return render_template('user/history.html', donations=donations)


# ==================== NGO ROUTES ====================

@app.route('/ngo/dashboard')
@login_required
@role_required('ngo')
def ngo_dashboard():
    """NGO dashboard"""
    nearby = get_nearby_donations(current_user.location)
    
    accepted = Donation.query.filter_by(accepted_by=current_user.id).order_by(Donation.updated_at.desc()).limit(5).all()
    
    stats = {
        'nearby_count': len(nearby),
        'accepted_count': Donation.query.filter_by(accepted_by=current_user.id, status='accepted').count(),
        'collected_count': Donation.query.filter_by(accepted_by=current_user.id, status='collected').count()
    }
    
    return render_template('ngo/dashboard.html', nearby=nearby, accepted=accepted, stats=stats)


@app.route('/ngo/nearby')
@login_required
@role_required('ngo')
def ngo_nearby():
    """View nearby donations"""
    time_filter = request.args.get('time', '')
    
    if time_filter:
        donations = get_nearby_donations(current_user.location, time_filter)
    else:
        donations = get_nearby_donations(current_user.location)
    
    return render_template('ngo/nearby.html', donations=donations)


@app.route('/ngo/accept/<int:donation_id>')
@login_required
@role_required('ngo')
def ngo_accept(donation_id):
    """Accept a donation"""
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != 'available':
        flash('This donation is no longer available.', 'warning')
        return redirect(url_for('ngo_nearby'))
    
    donation.status = 'accepted'
    donation.accepted_by = current_user.id
    donation.updated_at = datetime.utcnow()
    
    # Create request record
    req = Request(
        requester_id=current_user.id,
        requester_type='ngo',
        donation_id=donation.id,
        status='accepted'
    )
    db.session.add(req)
    db.session.commit()
    
    flash('Donation accepted! You can now contact the donor.', 'success')
    return redirect(url_for('ngo_dashboard'))


@app.route('/ngo/confirm/<int:donation_id>')
@login_required
@role_required('ngo')
def ngo_confirm(donation_id):
    """Confirm food pickup"""
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.accepted_by != current_user.id:
        flash('You do not have permission to confirm this donation.', 'danger')
        return redirect(url_for('ngo_dashboard'))
    
    donation.status = 'collected'
    donation.updated_at = datetime.utcnow()
    
    # Update request
    req = Request.query.filter_by(donation_id=donation.id, requester_id=current_user.id).first()
    if req:
        req.status = 'completed'
        req.pickup_confirmed = True
        req.confirmed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Pickup confirmed successfully!', 'success')
    return redirect(url_for('ngo_history'))


@app.route('/ngo/history')
@login_required
@role_required('ngo')
def ngo_history():
    """NGO donation history"""
    donations = Donation.query.filter_by(accepted_by=current_user.id).order_by(Donation.updated_at.desc()).all()
    return render_template('ngo/history.html', donations=donations)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    stats = get_donation_stats()
    
    users_count = User.query.count()
    ngos_count = NGO.query.count()
    pending_ngos = NGO.query.filter_by(is_verified=False).count()
    
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         users_count=users_count, 
                         ngos_count=ngos_count,
                         pending_ngos=pending_ngos,
                         recent_donations=recent_donations)


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/ngos')
@login_required
@role_required('admin')
def admin_ngos():
    """Manage NGOs"""
    ngos = NGO.query.order_by(NGO.created_at.desc()).all()
    return render_template('admin/ngos.html', ngos=ngos)


@app.route('/admin/verify/<int:ngo_id>')
@login_required
@role_required('admin')
def admin_verify_ngo(ngo_id):
    """Verify NGO"""
    ngo = NGO.query.get_or_404(ngo_id)
    ngo.is_verified = True
    ngo.verified_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'NGO "{ngo.ngo_name}" verified successfully!', 'success')
    return redirect(url_for('admin_ngos'))


@app.route('/admin/donations')
@login_required
@role_required('admin')
def admin_donations():
    """Monitor all donations"""
    status_filter = request.args.get('status', '')
    
    query = Donation.query
    
    if status_filter:
        query = query.filter(Donation.status == status_filter)
    
    donations = query.order_by(Donation.created_at.desc()).all()
    
    return render_template('admin/donations.html', donations=donations)


@app.route('/admin/remove/<int:donation_id>')
@login_required
@role_required('admin')
def admin_remove_donation(donation_id):
    """Remove fake/invalid donation"""
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    
    flash('Donation removed successfully!', 'success')
    return redirect(url_for('admin_donations'))


@app.route('/admin/check_expired')
@login_required
@role_required('admin')
def admin_check_expired():
    """Manually trigger expiry check"""
    count = check_expired_donations()
    flash(f'✅ Checked donations. Marked {count} as expired.', 'success')
    return redirect(url_for('admin_dashboard'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ==================== CLI COMMANDS ====================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    
    # Create default admin if not exists
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            email='admin@fooddonation.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Database initialized!')
        print('👤 Admin credentials: admin@fooddonation.com / admin123')
    else:
        print('✅ Database already initialized!')


@app.cli.command()
def check_expired():
    """Check and mark expired donations"""
    count = check_expired_donations()
    print(f'✅ Checked donations. Marked {count} as expired.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000)
