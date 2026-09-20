"""
Database seed script
"""
import sys
import os
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, Channel, ChannelType, Warehouse
from app.auth import get_password_hash
from app.config import settings

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@local")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123")
    staff_email = os.getenv("SEED_STAFF_EMAIL", "staff@local")
    staff_password = os.getenv("SEED_STAFF_PASSWORD", "Staff@123")
    
    try:
        # Create admin user
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                name="Admin User",
                password_hash=get_password_hash(admin_password),
                role=UserRole.ADMIN
            )
            db.add(admin)
            print(f"✅ Created admin user: {admin_email}")
        else:
            print(f"✅ Admin user ({admin_email}) already exists")
        
        # Create staff user
        staff = db.query(User).filter(User.email == staff_email).first()
        if not staff:
            staff = User(
                email=staff_email,
                name="Staff User",
                password_hash=get_password_hash(staff_password),
                role=UserRole.STAFF
            )
            db.add(staff)
            print(f"✅ Created staff user: {staff_email}")
        else:
            print(f"✅ Staff user ({staff_email}) already exists")
        
        # Create channels
        channels = [
            ChannelType.SHOPIFY,
            ChannelType.AMAZON,
            ChannelType.FLIPKART,
            ChannelType.MYNTRA
        ]
        
        for channel_type in channels:
            channel = db.query(Channel).filter(Channel.name == channel_type).first()
            if not channel:
                channel = Channel(name=channel_type, is_active=True)
                db.add(channel)
                print(f"✅ Created channel: {channel_type.value}")
            else:
                print(f"✅ Channel {channel_type.value} already exists")
        
        # Create default warehouse
        warehouse = db.query(Warehouse).filter(Warehouse.name == "Main Warehouse").first()
        if not warehouse:
            warehouse = Warehouse(
                name="Main Warehouse",
                city="Mumbai",
                state="Maharashtra"
            )
            db.add(warehouse)
            print("✅ Created warehouse: Main Warehouse")
        else:
            print("✅ Warehouse already exists")
        
        db.commit()
        print("\n🎉 Seeding completed!")
        print("\n📝 Login credentials:")
        print(f"   Admin: {admin_email}")
        print(f"   Staff: {staff_email}")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    force = "--force" in sys.argv
    if settings.IS_PRODUCTION and not force:
        print("🛑 Refusing to run seed.py in PRODUCTION environment without --force flag!")
        print("   If you intended to seed production data, set SEED_ADMIN_EMAIL & SEED_ADMIN_PASSWORD and run with --force.")
        sys.exit(1)

    print("🌱 Starting database seeding...")
    print("")
    
    # Test database connection first
    try:
        print("🔌 Testing database connection...")
        with engine.connect() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("")
        print("💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running:")
        print("      macOS: brew services start postgresql@14")
        print("      Linux: sudo systemctl start postgresql")
        print("")
        print("   2. Run the setup script:")
        print("      ./setup_local_db.sh")
        print("")
        print("   3. Check your DATABASE_URL in .env file")
        exit(1)
    
    print("")
    
    # Create tables
    try:
        print("📦 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created!")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        exit(1)
    
    print("")
    
    # Seed data
    seed_database()
