from datetime import datetime, timedelta
from app import app, db
from models import User, NGO, Admin, Donation
from werkzeug.security import generate_password_hash

def verify_setup():
    """Verify that the database is set up correctly with initial data"""
    with app.app_context():
        print("🔍 Checking database setup...")
        
        # 1. Check Tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        required_tables = ['user', 'ngo', 'admin', 'donation', 'request']
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            print(f"❌ Missing tables: {missing}")
            print("🛠️ Creating tables...")
            db.create_all()
            print("✅ Tables created successfully")
        else:
            print("✅ All tables present")
            
        # 2. Check Admin
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            print("⚠️ Admin user missing. Creating one now...")
            admin = Admin(
                username='admin',
                email='admin@fooddonation.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Created default admin: admin / admin123")
        else:
            print("✅ Admin user exists")
            
        # 3. Create Dummy Data for Testing
        if User.query.count() == 0:
            print("\n📝 Creating sample users...")
            donor = User(
                username='donor1',
                email='donor1@example.com',
                password_hash=generate_password_hash('password'),
                phone_number='9876543210',
                location='Chennai',
                role='donor'
            )
            db.session.add(donor)
            db.session.commit()
            print("✅ Created sample donor: donor1@example.com / password")
            
            # Create sample donation
            donation = Donation(
                donor_id=donor.id,
                food_name='Vegetable Biryani',
                quantity='25 packets',
                food_time='afternoon',
                expiry_datetime=datetime.utcnow() + timedelta(hours=4),
                location='Chennai',
                description='Freshly cooked veg biryani, ready for pickup'
            )
            db.session.add(donation)
            db.session.commit()
            print("✅ Created sample donation")
            
        return True

if __name__ == "__main__":
    verify_setup()
