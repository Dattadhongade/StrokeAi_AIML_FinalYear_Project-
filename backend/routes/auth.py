from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
from bson import ObjectId
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.utils.db import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Convert ObjectId to string for easy JSON serialization
        user["_id"] = str(user["_id"])
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLogin(BaseModel):
    credential: str

@router.post("/register")
async def register(user: UserRegister):
    db = get_db()
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "auth_provider": "local",
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    token = create_access_token(data={"sub": str(result.inserted_id)})
    return {"token": token, "user": {"id": str(result.inserted_id), "name": user.name, "email": user.email}}

@router.post("/login")
async def login(user: UserLogin):
    db = get_db()
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or db_user.get("auth_provider") != "local":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(db_user["_id"])})
    return {"token": token, "user": {"id": str(db_user["_id"]), "name": db_user["name"], "email": db_user["email"]}}

@router.post("/google")
async def google_auth(request: GoogleLogin):
    db = get_db()
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured on server")
        
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(request.credential, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = idinfo['email']
        name = idinfo.get('name', 'Google User')
        
        # Check if user exists
        user = await db.users.find_one({"email": email})
        
        if not user:
            # Register new Google user
            user_dict = {
                "name": name,
                "email": email,
                "auth_provider": "google",
                "created_at": datetime.utcnow()
            }
            result = await db.users.insert_one(user_dict)
            user_id = str(result.inserted_id)
        else:
            user_id = str(user["_id"])
            
        # Generate our own JWT token
        token = create_access_token(data={"sub": user_id})
        return {"token": token, "user": {"id": user_id, "name": name, "email": email}}
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": {
        "id": current_user["_id"],
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "auth_provider": current_user.get("auth_provider")
    }}
