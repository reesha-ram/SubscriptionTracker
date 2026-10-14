from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Users
from app.schemas import UserResponse, UserCreate, Token
from app.utils import decode_access_token, hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

templates = Jinja2Templates(directory="templates")

# auto_error=False prevents FastAPI from automatically raising a 401 when the header is missing,
# allowing us to inspect cookies first for Jinja2 page navigation.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

db_dependency = Annotated[Session, Depends(get_db)]

# ==========================================
# 1. AUTHENTICATION DEPENDENCY
# ==========================================

async def get_current_user(
    request: Request,
    token_header: Optional[str] = Depends(oauth2_bearer)
) -> dict:
    """
    Reads token from HTTP Cookie first (for Jinja2 browser page requests),
    or falls back to Authorization Header (for API fetch requests).
    """
    token = request.cookies.get("access_token") or token_header

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    username: Optional[str] = payload.get("sub")
    user_id: Optional[int] = payload.get("user_id")

    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user claims."
        )

    return {"username": username, "id": user_id}

# ==========================================
# 2. JINJA2 WEB PAGE ROUTES
# ==========================================

# Pass include_in_schema=False to hide HTML pages from Swagger docs
@router.get("/login-page", include_in_schema=False)
def render_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@router.get("/register-page", include_in_schema=False)
def render_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )

# ==========================================
# 3. API ENDPOINTS
# ==========================================

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(user_data: UserCreate, db: db_dependency):
    """Registers a new user after verifying unique email and username."""
    existing_email = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    existing_username = db.query(Users).filter(Users.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken."
        )

    new_user = Users(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        currency=user_data.currency or "INR",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    """Authenticates user credentials and returns a JWT access token."""
    user = db.query(Users).filter(Users.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}