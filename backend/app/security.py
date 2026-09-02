import secrets
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.config import settings

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Auth
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# API Key Generation for Chrome Extension
def generate_api_key() -> str:
    return f"ws_live_{secrets.token_hex(28)}"

# Global Fernet instance for predictable encryption/decryption
_fernet_instance = Fernet(Fernet.generate_key())

def encrypt_credential(plain_text: str) -> bytes:
    if not plain_text:
        return b""
    return _fernet_instance.encrypt(plain_text.encode())

def decrypt_credential(cipher_text: bytes) -> str:
    if not cipher_text:
        return ""
    try:
        return _fernet_instance.decrypt(cipher_text).decode()
    except Exception:
        return ""
