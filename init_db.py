#!/usr/bin/env python3
"""
Database initialization script for the Ecommerce Audit Logs application.
This script creates the database tables and optionally adds sample data.
"""

from app import app, db, Account, User, AuditLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    with app.app_context():
        # Create sample account
        account = Account(
            name="Sample Ecommerce Store",
            domain="sample-store.com"
        )
        db.session.add(account)
        db.session.flush()  # Get the account ID
        
        # Create owner user
        owner = User(
            email="owner@sample-store.com",
            password_hash=generate_password_hash("owner123"),
            first_name="John",
            last_name="Owner",
            role="owner",
            account_id=account.id
        )
        db.session.add(owner)
        
        # Create admin user
        admin = User(
            email="admin@sample-store.com",
            password_hash=generate_password_hash("admin123"),
            first_name="Jane",
            last_name="Admin",
            role="admin",
            account_id=account.id
        )
        db.session.add(admin)
        
        # Create analyst user
        analyst = User(
            email="analyst@sample-store.com",
            password_hash=generate_password_hash("analyst123"),
            first_name="Bob",
            last_name="Analyst",
            role="analyst",
            account_id=account.id
        )
        db.session.add(analyst)
        
        # Create content creator user
        content_creator = User(
            email="creator@sample-store.com",
            password_hash=generate_password_hash("creator123"),
            first_name="Alice",
            last_name="Creator",
            role="content_creator",
            account_id=account.id
        )
        db.session.add(content_creator)
        
        db.session.commit()
        
        # Create sample audit logs
        actions = [
            "user_login", "user_logout", "product_created", "product_updated",
            "order_created", "order_cancelled", "user_created", "user_updated",
            "inventory_updated", "price_changed", "category_created"
        ]
        
        resource_types = ["user", "product", "order", "inventory", "category"]
        
        users = [owner, admin, analyst, content_creator]
        
        # Generate sample audit logs for the past 30 days
        for i in range(100):
            user = random.choice(users)
            action = random.choice(actions)
            resource_type = random.choice(resource_types)
            
            # Create timestamp within the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            timestamp = datetime.utcnow() - timedelta(
                days=days_ago,
                hours=hours_ago,
                minutes=minutes_ago
            )
            
            audit_log = AuditLog(
                user_id=user.id,
                account_id=account.id,
                action=action,
                resource_type=resource_type,
                resource_id=str(random.randint(1, 1000)),
                details=f"Sample {action} action performed by {user.first_name} {user.last_name}",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                created_at=timestamp
            )
            db.session.add(audit_log)
        
        db.session.commit()
        print("Sample data created successfully!")
        print(f"Created account: {account.name} (ID: {account.id})")
        print(f"Created users:")
        print(f"  - Owner: {owner.email} (password: owner123)")
        print(f"  - Admin: {admin.email} (password: admin123)")
        print(f"  - Analyst: {analyst.email} (password: analyst123)")
        print(f"  - Content Creator: {content_creator.email} (password: creator123)")
        print(f"Created {100} sample audit logs")

if __name__ == "__main__":
    print("Initializing Ecommerce Audit Logs Database...")
    
    # Initialize database
    init_database()
    
    # Ask if user wants to create sample data
    response = input("\nDo you want to create sample data? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        create_sample_data()
    
    print("\nDatabase initialization complete!")
    print("You can now run the application with: python app.py") 