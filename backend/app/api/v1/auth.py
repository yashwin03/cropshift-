import app.patch_bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator

from app.database.session import get_db
from app.models.user import User, UserRole
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password: str
    role: Optional[str] = "FARMER"
    gst_number: Optional[str] = None

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v):
        if not v:
            return UserRole.FARMER.value
        val = str(v).upper()
        if val not in [r.value for r in UserRole]:
            raise ValueError(f"Invalid role '{v}'. Allowed roles are: FARMER, BUYER")
        return val

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: str
    role: UserRole
    farmer_id: Optional[str] = None
    partner_code: Optional[str] = None
    gst_number: Optional[str] = None
    gst_status: Optional[str] = None

    class Config:
        from_attributes = True

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username.ilike(username.strip())).first()
    if user is None:
        raise credentials_exception
    if user.role == UserRole.FARMER and not user.farmer_id:
        user.farmer_id = f"FS-{user.id:06d}"
        db.commit()
        db.refresh(user)
    elif user.role == UserRole.BUYER and not getattr(user, 'partner_code', None):
        user.partner_code = f"BUY-{user.id:04d}-KAR"
        db.commit()
        db.refresh(user)
    return user

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_role = getattr(current_user, 'role', UserRole.FARMER) or UserRole.FARMER
        user_role_str = (user_role.value if hasattr(user_role, 'value') else str(user_role)).upper()
        allowed_str = [(r.value if hasattr(r, 'value') else str(r)).upper() for r in allowed_roles]
        if user_role_str not in allowed_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role_str}' does not have required access permissions."
            )
        return current_user
    return role_checker


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    clean_username = user.username.strip()
    db_user = db.query(User).filter(User.username.ilike(clean_username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user_email = user.email.strip() if user.email and user.email.strip() else f"{clean_username}@cropshift.com"
    existing_email = db.query(User).filter(User.email.ilike(user_email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email address already registered")

    if user.phone and user.phone.strip():
        clean_phone = user.phone.strip()
        existing_phone = db.query(User).filter(User.phone == clean_phone).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Validate role enum
    role_str = (user.role or "FARMER").upper()
    try:
        user_role_enum = UserRole[role_str]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid role '{user.role}'. Allowed roles: FARMER, BUYER")

    hashed_password = get_password_hash(user.password)
    
    gst_num = user.gst_number.strip() if user.gst_number and user.gst_number.strip() else None
    gst_stat = "GST Provided" if gst_num else "Verification Pending"
    
    db_user = User(
        username=clean_username,
        email=user_email,
        hashed_password=hashed_password,
        role=user_role_enum,
        full_name=user.full_name.strip() if user.full_name else None,
        phone=user.phone.strip() if user.phone else None,
        gst_number=gst_num,
        gst_status=gst_stat if user_role_enum == UserRole.BUYER else None
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username, email, or phone number is already registered")

    if db_user.role == UserRole.FARMER and not db_user.farmer_id:
        db_user.farmer_id = f"FS-{db_user.id:06d}"
        db.commit()
        db.refresh(db_user)
    elif db_user.role == UserRole.BUYER and not getattr(db_user, 'partner_code', None):
        db_user.partner_code = f"BUY-{db_user.id:04d}-KAR"
        db.commit()
        db.refresh(db_user)

    return db_user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    clean_username = form_data.username.strip() if form_data.username else ""
    user = db.query(User).filter(User.username.ilike(clean_username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.role == UserRole.FARMER and not user.farmer_id:
        user.farmer_id = f"FS-{user.id:06d}"
        db.commit()
        db.refresh(user)

    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": role_str, "farmer_id": user.farmer_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

