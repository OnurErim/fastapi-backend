import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import UserModel, RoleEnum, PasswordModel
from schemas import RegisterRequest, LoginRequest, TokenResponse
from security import hash_password, verify_password, create_access_token

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register/email", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email zaten kayıtlı."
        )

    user = UserModel(
        email=data.email,
        full_name=data.full_name,
        role=RoleEnum.USER,
        phone="",
        linkedin="",
        institution="",
        profession="",
        sectors=[]
    )
    db.add(user)
    db.flush()

    password_entry = PasswordModel(
        user_id=user.id,
        hashed_password=hash_password(data.password)
    )
    db.add(password_entry)

    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenResponse(access_token=token)

@router.post("/login/email", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user or not user.password_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı."
        )

    if not verify_password(data.password, user.password_entry.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı."
        )

    token = create_access_token(user)
    return TokenResponse(access_token=token)

def create_admin_if_not_exists():
    from database import SessionLocal
    db = SessionLocal()

    admin = db.query(UserModel).filter(UserModel.email == ADMIN_EMAIL).first()

    if not admin:
        admin = UserModel(
            email=ADMIN_EMAIL,
            full_name="Admin",
            role=RoleEnum.ADMIN,
            phone="",
            linkedin="",
            institution="",
            profession="",
            sectors=[]
        )
        db.add(admin)
        db.flush()

    if not admin.password_entry:
        password_entry = PasswordModel(
            user_id=admin.id,
            hashed_password=hash_password(ADMIN_PASSWORD)
        )
        db.add(password_entry)

    db.commit()
    db.refresh(admin)
    db.close()