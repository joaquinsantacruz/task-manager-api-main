from datetime import datetime, timedelta, timezone
from typing import Any, Union
import jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Generate a signed JSON Web Token (JWT) for authentication.
    
    This function creates a JWT containing the subject (typically user ID) and
    an expiration time. The token is signed using the application's secret key
    and can be used for stateless authentication.
    
    Args:
        subject: The subject of the token, typically a user ID or email.
                Can be any type but will be converted to string.
        expires_delta: Custom token expiration time. If not provided, defaults
                      to ACCESS_TOKEN_EXPIRE_MINUTES from settings.
    
    Returns:
        str: Signed JWT token as a string that can be included in Authorization headers
    
    Token Structure:
        - exp: Expiration timestamp (UTC)
        - sub: Subject identifier (user ID)
    
    Security Notes:
        - Tokens are signed with HMAC-SHA256 (or algorithm from settings)
        - Secret key is loaded from environment configuration
        - Tokens expire automatically based on timestamp
        - All timestamps are in UTC timezone
    
    Example:
        >>> token = create_access_token(subject=user.id)
        >>> # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed version.
    
    This function uses the Argon2 hashing algorithm to securely compare
    a plain text password with its stored hash. It's designed to be
    resistant to timing attacks.
    
    Args:
        plain_password: The plain text password provided by the user during login
        hashed_password: The hashed password stored in the database
    
    Returns:
        bool: True if the password matches the hash, False otherwise
    
    Security Notes:
        - Uses Argon2 algorithm (memory-hard, resistant to GPU attacks)
        - Constant-time comparison to prevent timing attacks
        - Does not reveal why verification failed (same response for wrong password or invalid hash)
    
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a secure hash of a password using Argon2 algorithm.
    
    This function hashes a plain text password for secure storage in the database.
    The resulting hash includes the salt and algorithm parameters, making it
    self-contained and verifiable.
    
    Args:
        password: Plain text password to hash (will never be stored directly)
    
    Returns:
        str: Hashed password string in Argon2 format, including:
            - Algorithm identifier
            - Cost parameters (memory, iterations)
            - Random salt
            - Resulting hash
    
    Security Notes:
        - Uses Argon2 (winner of Password Hashing Competition 2015)
        - Automatically generates random salt for each hash
        - Memory-hard algorithm resistant to GPU/ASIC attacks
        - Hash output is different even for identical passwords (due to random salt)
        - Safe to store in database (original password cannot be recovered)
    
    Example:
        >>> hash1 = get_password_hash("mypassword")
        >>> hash2 = get_password_hash("mypassword")
        >>> hash1 != hash2  # Different hashes due to random salts
        True
    """
    return pwd_context.hash(password)