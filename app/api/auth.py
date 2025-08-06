"""
Authentication API endpoints for Legal Dashboard
================================================
Provides user authentication, JWT token management, and role-based access control.
"""

import os
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import sqlite3
from contextlib import contextmanager

# ─────────────────────────────
# Logging configuration
# ─────────────────────────────
logger = logging.getLogger(__name__)

# ─────────────────────────────
# Security configuration
# ─────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing with fixed bcrypt version handling
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test bcrypt to avoid runtime errors
    pwd_context.hash("test")
    logger.info("✅ bcrypt initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ bcrypt initialization issue: {e}")
    # Fallback to a working bcrypt configuration
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Security scheme
security = HTTPBearer()

# ─────────────────────────────
# Database path configuration with fallback
# ─────────────────────────────
def get_database_path():
    """Get database path with fallback options for different environments"""
    # Try environment variable first
    db_dir = os.getenv("DATABASE_DIR", "/app/data")
    db_name = os.getenv("DATABASE_NAME", "legal_documents.db")
    
    # List of possible directories to try
    possible_dirs = [
        db_dir,
        "/app/data",
        "/app/database", 
        "/tmp/app_fallback",
        tempfile.gettempdir() + "/legal_dashboard"
    ]
    
    for directory in possible_dirs:
        try:
            # Try to create directory
            Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = Path(directory) / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            db_path = Path(directory) / db_name
            logger.info(f"Using database directory: {directory}")
            return str(db_path)
            
        except (PermissionError, OSError) as e:
            logger.warning(f"Cannot use directory {directory}: {e}")
            continue
    
    # Final fallback - in-memory database
    logger.warning("Using in-memory SQLite database - data will not persist!")
    return ":memory:"

DB_PATH = get_database_path()

# ─────────────────────────────
# Pydantic models
# ─────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# ─────────────────────────────
# Database connection
# ─────────────────────────────
@contextmanager
def get_db_connection():
    """Database connection with error handling"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        if conn:
            conn.close()

# ─────────────────────────────
# Initialize database tables
# ─────────────────────────────
def init_auth_tables():
    """Initialize authentication tables with error handling"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    refresh_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            """)
            
            # Create default admin user if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                hashed_password = pwd_context.hash("admin123")
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, role)
                    VALUES (?, ?, ?, ?)
                """, ("admin", "admin@legal-dashboard.com", hashed_password, "admin"))
                logger.info("Default admin user created (username: admin, password: admin123)")
            
            conn.commit()
            logger.info("Authentication tables initialized successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize auth tables: {e}")
        raise

# ─────────────────────────────
# Password utilities
# ─────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

# ─────────────────────────────
# Token utilities
# ─────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.debug(f"Token verification failed: {e}")
        return None

# ─────────────────────────────
# User utilities
# ─────────────────────────────
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Error updating last login: {e}")

def log_auth_attempt(user_id: Optional[int], action: str, success: bool,
                     ip_address: str = None, user_agent: str = None, details: str = None):
    """Log authentication attempt"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO auth_audit_log (user_id, action, ip_address, user_agent, success, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, ip_address, user_agent, success, details))
            conn.commit()
    except Exception as e:
        logger.error(f"Error logging auth attempt: {e}")

# ─────────────────────────────
# Authentication dependency
# ─────────────────────────────
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = get_user_by_id(int(payload.get("sub")))
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

def require_role(required_role: str):
    """Require specific role for endpoint access"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        if user_role not in ("admin", required_role) and required_role != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# ─────────────────────────────
# API Router
# ─────────────────────────────
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if username already exists
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, role)
                VALUES (?, ?, ?, ?)
            """, (user_data.username, user_data.email, hashed_password, user_data.role))
            user_id = cursor.lastrowid
            conn.commit()
        
        user = get_user_by_id(user_id)
        log_auth_attempt(user_id, "register", True)
        return UserResponse(**user)
        
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """User login"""
    user = get_user_by_username(user_credentials.username)
    
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        log_auth_attempt(user["id"] if user else None, "login", False, details="Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.get("is_active"):
        log_auth_attempt(user["id"], "login", False, details="Account inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Update last login
    update_last_login(user["id"])
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user["id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    # Store refresh token
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (user_id, refresh_token, expires_at) 
                VALUES (?, ?, ?)
            """, (
                user["id"], 
                refresh_token, 
                (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to store refresh token: {e}")
    
    log_auth_attempt(user["id"], "login", True)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    payload = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    
    # Verify refresh token exists and is valid
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE refresh_token = ? AND expires_at > ? AND user_id = ?
            """, (refresh_token, datetime.utcnow().isoformat(), user_id))
            
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )
    except Exception as e:
        logger.error(f"Refresh token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed"
        )
    
    # Create new tokens
    new_access = create_access_token(data={"sub": str(user_id)})
    new_refresh = create_refresh_token(data={"sub": str(user_id)})
    
    # Update refresh token in database
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET refresh_token = ?, expires_at = ? 
                WHERE refresh_token = ?
            """, (
                new_refresh,
                (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat(),
                refresh_token
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to update refresh token: {e}")
    
    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """User logout"""
    try:
        # Clean up user sessions
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE user_id = ?", (current_user["id"],))
            conn.commit()
    except Exception as e:
        logger.error(f"Logout cleanup failed: {e}")
    
    log_auth_attempt(current_user["id"], "logout", True)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password"""
    if not verify_password(password_data.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    new_hash = get_password_hash(password_data.new_password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET hashed_password = ? WHERE id = ?", 
                (new_hash, current_user["id"])
            )
            conn.commit()
        
        log_auth_attempt(current_user["id"], "password_change", True)
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/users", response_model=list[UserResponse])
async def get_users(current_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Get all users (admin only)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = [dict(row) for row in cursor.fetchall()]
        
        return [UserResponse(**user) for user in users]
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

# ─────────────────────────────
# Initialize tables on module import
# ─────────────────────────────
try:
    init_auth_tables()
except Exception as e:
    logger.error(f"Failed to initialize authentication system: {e}")
    # Don't raise here to allow the app to start even if DB init fails