"""
Authentication service and FastAPI dependencies.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import get_db
from app.db.models import UserModel
from app.db.user import UserRepository

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_auth_scheme = APIKeyHeader(
    name="Authorization",
    auto_error=False,
    scheme_name="Authorization",
    description="Paste only the JWT token value.",
)
bypass_auth_scheme = APIKeyHeader(
    name="X-Bypass-Key",
    auto_error=False,
    scheme_name="X-Bypass-Key",
    description="Paste only the bypass key value.",
)


class AuthService:
    """
    Service for registering users, validating credentials, and creating tokens.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, email: str, password: str) -> UserModel:
        """
        Create a new user with a hashed password.
        """
        normalized_email = email.lower()
        existing_user = self.user_repo.get_by_email(normalized_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        password_hash = self.hash_password(password)
        return self.user_repo.create_user(normalized_email, password_hash)

    def authenticate_user(self, email: str, password: str) -> UserModel:
        """
        Validate credentials and return the matching user.
        """
        normalized_email = email.lower()
        user = self.user_repo.get_by_email(normalized_email)
        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password with bcrypt.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a plain-text password against its stored hash.
        """
        return pwd_context.verify(password, password_hash)

    @staticmethod
    def create_access_token(user: UserModel) -> str:
        """
        Create a signed JWT access token for the user.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": user.id,
            "email": user.email,
            "exp": expire,
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )


def is_bypass_user(user: UserModel) -> bool:
    """Return True when the authenticated user is the local bypass user."""
    return user.email.lower() == settings.LOCAL_BYPASS_EMAIL.lower()


def get_current_user(
    authorization: str | None = Depends(bearer_auth_scheme),
    bypass_key: str | None = Depends(bypass_auth_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    """
    Decode the Authorization header and load the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if bypass_key == settings.LOCAL_BYPASS_KEY:
        user_repo = UserRepository(db)
        bypass_user = user_repo.get_by_email(settings.LOCAL_BYPASS_EMAIL.lower())
        if bypass_user:
            logger.info("Authenticated local bypass user")
            return bypass_user

        bypass_user = user_repo.create_user(
            settings.LOCAL_BYPASS_EMAIL.lower(),
            AuthService.hash_password(settings.LOCAL_BYPASS_KEY),
        )
        logger.info("Created and authenticated local bypass user")
        return bypass_user

    if authorization is None:
        raise credentials_exception

    scheme, _, token = authorization.partition(" ")
    jwt_token = token if scheme.lower() == "bearer" and token else authorization

    try:
        payload = jwt.decode(
            jwt_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        logger.warning("Failed JWT validation")
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise credentials_exception

    return user
