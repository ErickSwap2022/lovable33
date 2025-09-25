import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    async def get_user_by_email(self, email: str):
        user = await self.db.users.find_one({"email": email})
        return user
    
    async def get_user_by_id(self, user_id: str):
        user = await self.db.users.find_one({"id": user_id})
        return user
    
    async def create_user(self, user_data: dict):
        # Hash password
        user_data["hashed_password"] = self.get_password_hash(user_data.pop("password"))
        
        # Check if user exists
        existing_user = await self.get_user_by_email(user_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        result = await self.db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        
        # Remove the MongoDB ObjectId to avoid serialization issues
        user_data.pop("_id", None)
        
        return user_data
    
    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if not user:
            return False
        if not self.verify_password(password, user.get("hashed_password", "")):
            return False
        
        # Convert ObjectId to string and remove _id field
        if "_id" in user:
            user["id"] = str(user["_id"])
            user.pop("_id", None)
        
        return user