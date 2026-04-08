"""
Update existing patient names in the database to South Indian names
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)  # Change to backend directory for database access

from database import SessionLocal
from models import User

# Name mapping from old to new
NAME_MAPPING = {
    "Tony Stark": "Arjun Menon",
    "John Doe": "Ramesh Naidu",
    "Sarah Connor": "Lakshmi Devi",
    "Bruce Wayne": "Rajesh Kumar",
    "Clark Kent": "Venkatesh Reddy",
    "Diana Prince": "Meenakshi Iyer",
    "Peter Parker": "Karthik Krishnan",
    "Wanda Maximoff": "Priya Nair",
    "Steve Rogers": "Suresh Babu",
    "Natasha Romanoff": "Kavitha Menon",
    "Jane Smith": "Saraswathi Amma",
    "Bob Johnson": "Arun Prasad",
    "Alice Brown": "Padmavathi Reddy",
    "Charlie Davis": "Vijay Shankar",
    "Dr. Sarah Wilson": "Dr. Divya Srinivasan"
}

def update_patient_names():
    """Update all patient names in the database"""
    session = SessionLocal()
    
    try:
        print("🔄 Updating patient names to South Indian names...")
        print("-" * 60)
        
        updated_count = 0
        
        # Get all users
        users = session.query(User).all()
        
        for user in users:
            if user.name in NAME_MAPPING:
                old_name = user.name
                new_name = NAME_MAPPING[old_name]
                user.name = new_name
                
                # Update email if it's based on the old name
                if old_name.lower().replace(" ", ".") in user.email.lower():
                    # Create new email from new name
                    new_email_prefix = new_name.lower().replace(" ", ".").replace("dr. ", "")
                    domain = user.email.split("@")[1]
                    user.email = f"{new_email_prefix}@{domain}"
                    print(f"✅ Updated: {old_name:20} → {new_name:20} ({user.email})")
                else:
                    print(f"✅ Updated: {old_name:20} → {new_name:20}")
                
                updated_count += 1
        
        session.commit()
        
        print("-" * 60)
        print(f"✨ Successfully updated {updated_count} patient names!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    update_patient_names()
