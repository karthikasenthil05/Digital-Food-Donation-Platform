from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User, NGO, Admin

class UserRegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    location = SelectField('Location', validators=[DataRequired()], choices=[
        ('Chennai', 'Chennai'),
        ('Coimbatore', 'Coimbatore'),
        ('Madurai', 'Madurai'),
        ('Trichy', 'Trichy'),
        ('Salem', 'Salem'),
        ('Tirunelveli', 'Tirunelveli'),
        ('Erode', 'Erode'),
        ('Vellore', 'Vellore'),
        ('Thoothukudi', 'Thoothukudi'),
        ('Thanjavur', 'Thanjavur')
    ])
    role = SelectField('I am a', validators=[DataRequired()], choices=[
        ('donor', 'Donor (I want to donate food)'),
        ('recipient', 'Recipient (I need food)')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        ngo = NGO.query.filter_by(email=email.data).first()
        if user or ngo:
            raise ValidationError('Email already registered. Please use a different one.')


class NGORegistrationForm(FlaskForm):
    """NGO registration form"""
    ngo_name = StringField('NGO Name', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    location = SelectField('Location', validators=[DataRequired()], choices=[
        ('Chennai', 'Chennai'),
        ('Coimbatore', 'Coimbatore'),
        ('Madurai', 'Madurai'),
        ('Trichy', 'Trichy'),
        ('Salem', 'Salem'),
        ('Tirunelveli', 'Tirunelveli'),
        ('Erode', 'Erode'),
        ('Vellore', 'Vellore'),
        ('Thoothukudi', 'Thoothukudi'),
        ('Thanjavur', 'Thanjavur')
    ])
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(min=5, max=50)])
    address = TextAreaField('Address', validators=[DataRequired()])
    submit = SubmitField('Register NGO')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        ngo = NGO.query.filter_by(email=email.data).first()
        if user or ngo:
            raise ValidationError('Email already registered. Please use a different one.')
    
    def validate_registration_number(self, registration_number):
        ngo = NGO.query.filter_by(registration_number=registration_number.data).first()
        if ngo:
            raise ValidationError('Registration number already exists.')


class LoginForm(FlaskForm):
    """Login form for all users"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('Login as', validators=[DataRequired()], choices=[
        ('user', 'User (Donor/Recipient)'),
        ('ngo', 'NGO'),
        ('admin', 'Admin')
    ])
    submit = SubmitField('Login')


class DonationForm(FlaskForm):
    """Food donation form"""
    food_name = StringField('Food Name', validators=[DataRequired(), Length(max=150)])
    quantity = StringField('Quantity (e.g., 10 kg, 50 plates)', validators=[DataRequired(), Length(max=50)])
    food_time = SelectField('Food Time', validators=[DataRequired()], choices=[
        ('morning', 'Morning (6 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 6 PM)'),
        ('night', 'Night (6 PM - 11 PM)')
    ])
    expiry_datetime = DateTimeLocalField('Expiry Date & Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    location = SelectField('Pickup Location', validators=[DataRequired()], choices=[
        ('Chennai', 'Chennai'),
        ('Coimbatore', 'Coimbatore'),
        ('Madurai', 'Madurai'),
        ('Trichy', 'Trichy'),
        ('Salem', 'Salem'),
        ('Tirunelveli', 'Tirunelveli'),
        ('Erode', 'Erode'),
        ('Vellore', 'Vellore'),
        ('Thoothukudi', 'Thoothukudi'),
        ('Thanjavur', 'Thanjavur')
    ])
    description = TextAreaField('Additional Details (Optional)')
    submit = SubmitField('Post Donation')
