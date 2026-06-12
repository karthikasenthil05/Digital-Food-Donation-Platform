from datetime import datetime
from models import Donation, db

def check_expired_donations():
    """Check and update expired donations"""
    expired_donations = Donation.query.filter(
        Donation.expiry_datetime < datetime.utcnow(),
        Donation.status == 'available'
    ).all()
    
    count = 0
    for donation in expired_donations:
        donation.status = 'expired'
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"✅ Marked {count} donations as expired")
    
    return count


def get_nearby_donations(location, food_time=None):
    """Get available donations by location and optionally by food time"""
    query = Donation.query.filter(
        Donation.location == location,
        Donation.status == 'available',
        Donation.expiry_datetime > datetime.utcnow()
    )
    
    if food_time:
        query = query.filter(Donation.food_time == food_time)
    
    return query.order_by(Donation.expiry_datetime.asc()).all()


def get_donation_stats():
    """Get donation statistics for admin dashboard"""
    from sqlalchemy import func
    
    total_donations = Donation.query.count()
    available = Donation.query.filter_by(status='available').count()
    accepted = Donation.query.filter_by(status='accepted').count()
    collected = Donation.query.filter_by(status='collected').count()
    expired = Donation.query.filter_by(status='expired').count()
    
    # Donations by location
    by_location = db.session.query(
        Donation.location,
        func.count(Donation.id).label('count')
    ).group_by(Donation.location).all()
    
    return {
        'total': total_donations,
        'available': available,
        'accepted': accepted,
        'collected': collected,
        'expired': expired,
        'by_location': dict(by_location)
    }


def format_time_ago(dt):
    """Format datetime to human-readable time ago"""
    if not dt:
        return "N/A"
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"


def format_time_remaining(dt):
    """Format datetime to time remaining"""
    if not dt:
        return "N/A"
    
    now = datetime.utcnow()
    diff = dt - now
    
    if diff.total_seconds() < 0:
        return "Expired"
    
    seconds = diff.total_seconds()
    
    if seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} min remaining"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} remaining"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} remaining"
