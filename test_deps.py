try:
    from passlib.context import CryptContext
    print("✅ passlib imported")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("test")
    print(f"✅ hashing works: {hash}")
except Exception as e:
    print(f"❌ passlib error: {e}")

try:
    from pydantic import EmailStr
    print("✅ pydantic EmailStr imported")
except Exception as e:
    print(f"❌ pydantic error: {e}")
