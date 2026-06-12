from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for donors and recipients"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'donor' or 'recipient'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='donor', lazy=True, foreign_keys='Donation.donor_id')
    
    def __repr__(self):
        return f'<User {self.username}>'


class NGO(db.Model, UserMixin):
    """NGO model for organizations"""
    __tablename__ = 'ngo'
    
    id = db.Column(db.Integer, primary_key=True)
    ngo_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NGO {self.ngo_name}>'


class Admin(db.Model, UserMixin):
    """Admin model"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Donation(db.Model):
    """Donation model for food donations"""
    __tablename__ = 'donation'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    food_time = db.Column(db.String(20), nullable=False)  # morning/afternoon/night
    expiry_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='available')  # available/accepted/collected/expired
    accepted_by = db.Column(db.Integer, db.ForeignKey('ngo.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requests = db.relationship('Request', backref='donation', lazy=True)
    acceptor = db.relationship('NGO', backref='accepted_donations', foreign_keys=[accepted_by])
    
    def __repr__(self):
        return f'<Donation {self.food_name}>'
    
    def is_expired(self):
        """Check if donation is expired"""
        return datetime.utcnow() > self.expiry_datetime


class Request(db.Model):
    """Request model for food requests"""
    __tablename__ = 'request'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, nullable=False)
    requester_type = db.Column(db.String(10), nullable=False)  # 'user' or 'ngo'
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/accepted/rejected/completed
    pickup_confirmed = db.Column(db.Boolean, default=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Request {self.id} for Donation {self.donation_id}>'
