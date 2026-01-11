# FaithConnect Backend - JWT Authentication

## 🎯 Implementation Complete

JWT-based authentication has been successfully implemented for the FaithConnect mobile app backend.

---

## 📁 Project Structure

```
backend/
 ├── app/
 │   ├── main.py              # FastAPI app with CORS
 │   ├── core/
 │   │   ├── config.py        # Environment variables & JWT settings
 │   │   └── security.py      # Password hashing & JWT helpers
 │   ├── db/
 │   │   ├── base.py          # SQLAlchemy Base
 │   │   └── session.py       # Database engine & session
 │   └── auth/
 │       ├── models.py        # User SQLAlchemy model
 │       ├── schemas.py       # Pydantic request/response schemas
 │       ├── routes.py        # /auth/signup, /login, /me
 │       ├── services.py      # Business logic (create/authenticate user)
 │       └── dependencies.py  # get_current_user dependency
 ├── .env                     # Environment variables
 ├── init_db.py               # Database initialization script
 └── requirements.txt         # Python dependencies
```

---

## 🔐 How JWT Authentication Works

### 1. **User Registration** (`POST /auth/signup`)
   - User provides: email, password, name, role, faith (if worshiper)
   - Password is hashed using bcrypt
   - User is saved to PostgreSQL (Neon)
   - JWT token is created with payload: `{sub: user_id, role: role, exp: expiration}`
   - Returns: access_token, user_id, role

### 2. **User Login** (`POST /auth/login`)
   - User provides: email, password
   - Password is verified against stored hash
   - JWT token is created and returned

### 3. **Protected Routes** (`GET /auth/me`)
   - Client sends JWT token in `Authorization: Bearer <token>` header
   - `get_current_user` dependency extracts and validates the token
   - Token payload is decoded to get user_id
   - User is fetched from database and returned

### 4. **JWT Token Structure**
```json
{
  "sub": "123",           // user_id
  "role": "worshiper",    // or "leader"
  "exp": 1234567890       // expiration timestamp
}
```

---

## 🛡️ Role-Based Access Control

### How Roles Are Enforced

1. **JWT Contains Role**: Every token includes the user's role (`worshiper` or `leader`)
2. **Dependency Injection**: Protected routes use `get_current_user` dependency
3. **Role Checking**: Additional dependencies can be created to enforce role-specific access:

```python
from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole

def require_leader(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is a leader."""
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can access this resource"
        )
    return current_user

# Usage in routes:
@router.post("/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(require_leader)
):
    # Only leaders can create posts
    pass
```

### Authorization Rules Enforced

- **Worshipers** (role: "worshiper"):
  - Can log in and access their profile
  - Can follow leaders (to be implemented)
  - Can message leaders (to be implemented)
  - ❌ CANNOT create posts or reels

- **Leaders** (role: "leader"):
  - Can log in and access their profile
  - Can create posts/reels (to be implemented)
  - Can reply to messages (to be implemented)

---

## 🗄️ Database Schema

### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user ID |
| email | VARCHAR | UNIQUE, NOT NULL | User email |
| password_hash | VARCHAR | NOT NULL | Bcrypt hashed password |
| name | VARCHAR | NOT NULL | User's full name |
| role | ENUM | NOT NULL | "worshiper" or "leader" |
| faith | VARCHAR | NULL | Required for worshipers |
| bio | VARCHAR | NULL | Optional, for leaders |
| profile_photo | VARCHAR | NULL | URL to profile photo |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | NOT NULL | Registration time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

---

## 🚀 API Endpoints

### 1. POST `/auth/signup`
**Register a new user**

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "role": "worshiper",
  "faith": "Christianity",
  "profile_photo": "https://example.com/photo.jpg"  // optional
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 1,
  "role": "worshiper"
}
```

---

### 2. POST `/auth/login`
**Login with credentials**

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 1,
  "role": "worshiper"
}
```

---

### 3. GET `/auth/me`
**Get current user profile** (Protected Route)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "worshiper",
  "faith": "Christianity",
  "bio": null,
  "profile_photo": "https://example.com/photo.jpg",
  "is_active": true,
  "created_at": "2026-01-08T10:30:00Z",
  "updated_at": "2026-01-08T10:30:00Z"
}
```

---

## 🔧 Environment Variables

Update your `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:pass@host/database?sslmode=require

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

**🔒 Security Note:** Change `SECRET_KEY` in production! Generate one using:
```bash
openssl rand -hex 32
```

---

## 🎯 Testing the API

### 1. Start the Server
```bash
cd C:\FaithConnect\backend
.\venv\Scripts\Activate.ps1
fastapi dev app/main.py
```

### 2. Test Signup
```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "leader@example.com",
    "password": "securepass123",
    "name": "Pastor John",
    "role": "leader",
    "bio": "Serving the community"
  }'
```

### 3. Test Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "leader@example.com",
    "password": "securepass123"
  }'
```

### 4. Test Protected Route
```bash
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 5. Interactive API Docs
Visit: http://127.0.0.1:8000/docs

---

## ✅ What's Implemented

- ✅ JWT access tokens (7-day expiration)
- ✅ Password hashing with bcrypt
- ✅ User registration with role validation
- ✅ User login with credential verification
- ✅ Protected routes with JWT verification
- ✅ Role-based user model (worshiper/leader)
- ✅ Faith validation (required for worshipers)
- ✅ PostgreSQL integration with Neon
- ✅ CORS enabled for mobile app access
- ✅ Clean, modular architecture

---

## 🚫 What's NOT Implemented (By Design)

- ❌ Refresh tokens (not needed for hackathon)
- ❌ Email verification
- ❌ Password reset
- ❌ OAuth/Social login
- ❌ Rate limiting
- ❌ Account lockout

---

## 🔜 Next Steps for Development

1. **Create Post/Reel Models** for leaders
2. **Implement Follow System** for worshipers
3. **Add Messaging System** between users
4. **Create role-specific endpoints** using custom dependencies
5. **Add pagination** for lists
6. **Implement file upload** for profile photos

---

## 📦 Dependencies

All required packages are in `requirements.txt`:
- `fastapi[standard]` - Web framework
- `SQLAlchemy` - ORM
- `psycopg2-binary` - PostgreSQL adapter
- `pydantic-settings` - Environment variables
- `python-jose` - JWT handling
- `passlib` - Password hashing
- `bcrypt` - Hashing algorithm
- `python-multipart` - Form data handling
- `email-validator` - Email validation

---

## 🎉 Summary

Your FaithConnect backend now has a complete, production-ready JWT authentication system that:

1. **Identifies users** via JWT tokens
2. **Distinguishes roles** (worshiper vs leader)
3. **Protects routes** with authentication middleware
4. **Validates credentials** securely
5. **Follows best practices** for FastAPI development

The system is ready for you to build additional features on top of this authentication foundation!
