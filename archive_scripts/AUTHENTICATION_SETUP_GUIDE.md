# Promethean Light - Authentication System Setup Guide

## 🎯 What's Been Built

I've created a complete authentication system for Promethean Light with:

### ✅ Features Implemented

1. **User Registration**
   - Email-based registration
   - Restricted to @vysusgroup.com domain
   - Email verification required
   - Password strength validation

2. **Email Verification**
   - Verification link sent to user email
   - 24-hour token expiration
   - Welcome email after verification
   - Admin notification when users register

3. **Login/Logout**
   - Secure password hashing (bcrypt)
   - JWT token-based sessions
   - HTTP-only cookies for security
   - 24-hour session duration

4. **Password Reset**
   - "Forgot password" workflow
   - Email reset link
   - 1-hour token expiration
   - All sessions invalidated after reset

5. **Web UI**
   - Beautiful login/register page
   - Search interface (after login)
   - Responsive design
   - Modern gradient styling

6. **Admin Notifications**
   - Email sent to you (Chris) when someone registers
   - Includes user name, email, timestamp
   - Auto-approved users (as requested)

7. **Security**
   - Password hashing with bcrypt
   - JWT tokens
   - HTTP-only cookies
   - Session tracking
   - Login attempt logging

---

## 📂 Files Created

### Backend
- `mydata/auth_models.py` - User, Session, LoginAttempt database models
- `mydata/auth_service.py` - Authentication logic (register, login, verify, etc.)
- `mydata/auth_api.py` - FastAPI authentication endpoints
- `mydata/email_service.py` - Email sending (Office 365 SMTP)

### Frontend
- `mydata/static/index.html` - Login/Register page
- `mydata/static/search.html` - Search interface (after login)
- `mydata/static/verify.html` - Email verification page
- `mydata/static/reset-password.html` - Password reset page

---

## ⚙️ Configuration Required

### Step 1: Install Required Packages

```bash
pip install passlib[bcrypt] pyjwt python-jose[cryptography]
```

### Step 2: Set Environment Variables

Create a file named `.env` in `C:\Code\Promethian Light\` with:

```env
# Email Configuration (Office 365)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your-email@vysusgroup.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@vysusgroup.com
ADMIN_EMAIL=chris.marinelli@vysusgroup.com

# Base URL for links in emails
BASE_URL=http://10.210.250.5:8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

**IMPORTANT: Getting Office 365 App Password**
1. Go to https://account.microsoft.com/security
2. Navigate to "Advanced security options"
3. Under "App passwords", create a new app password
4. Use this password in `SMTP_PASSWORD` (not your regular password)

---

## 🔧 Integration Steps

### Step 1: Update Database to Include Auth Tables

The authentication system requires new database tables. Run this migration:

```python
from mydata.database import Database
from mydata.auth_models import User, UserSession, LoginAttempt
from sqlmodel import SQLModel

# Create tables
db = Database()
engine = db.engine
SQLModel.metadata.create_all(engine)
```

### Step 2: Integrate Auth API into Main API

Update `mydata/api.py` to include:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .auth_api import router as auth_router

# Add authentication router
app.include_router(auth_router)

# Serve static files
app.mount("/static", StaticFiles(directory="mydata/static"), name="static")

# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse("mydata/static/index.html")

# Serve search page (protected)
@app.get("/search")
async def serve_search():
    return FileResponse("mydata/static/search.html")
```

### Step 3: Protect Existing API Endpoints

Update existing endpoints to require authentication:

```python
from .auth_api import get_current_user
from .auth_models import User

@app.get("/api/search")
async def search(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    # Your existing search logic
    pass
```

---

## 📱 User Experience Flow

### For New Users

1. **Visit:** `http://10.210.250.5:8000`
2. **Click:** "Register" tab
3. **Fill in:**
   - Full name
   - Email (@vysusgroup.com)
   - Password (min 8 characters)
   - Confirm password
4. **Submit:** Registration form
5. **Check email:** Verification link sent
6. **Click link:** Email verified
7. **Login:** Use credentials to access
8. **Start searching!**

### For Admin (Chris)

When someone registers:
1. **Receive email:** "New User Registration: [Name]"
2. **Email includes:**
   - User's full name
   - User's email
   - Registration timestamp
   - Status (pending verification)
3. **User is auto-approved** (as requested)
4. **They just need to verify email**

---

## 🌐 URLs for Your Team

**Login/Register:**
```
http://10.210.250.5:8000
http://VYSUSGROUPdzZSm:8000
```

**API Endpoints (after login):**
```
POST /auth/register - Register new user
POST /auth/login - Login
POST /auth/logout - Logout
GET /auth/me - Get current user info
GET /auth/verify?token=... - Verify email
POST /auth/request-password-reset - Request password reset
POST /auth/reset-password - Reset password

GET /api/search?q=query - Search (requires auth)
GET /api/stats - Statistics (requires auth)
GET /api/recent - Recent documents (requires auth)
```

---

## 🔐 Security Features

### Passwords
- Hashed with bcrypt (industry standard)
- Minimum 8 characters
- Never stored in plain text

### Sessions
- JWT tokens
- HTTP-only cookies (can't be accessed by JavaScript)
- 24-hour expiration
- Tracked in database

### Email Verification
- Required before access
- 24-hour token expiration
- Secure random tokens

### Password Reset
- 1-hour token expiration
- All sessions invalidated after reset
- Email-only delivery

### Domain Restriction
- Only @vysusgroup.com emails allowed
- Validated server-side

---

## 🧪 Testing Checklist

### Before Going Live

1. **Test Registration**
   ```
   - Visit http://10.210.250.5:8000
   - Register with @vysusgroup.com email
   - Check email for verification link
   - Verify email works
   ```

2. **Test Login**
   ```
   - Login with verified account
   - Check redirected to search page
   - Check cookie set in browser
   ```

3. **Test Search (Authenticated)**
   ```
   - Perform a search
   - View results
   - Check only authenticated users can access
   ```

4. **Test Logout**
   ```
   - Click logout
   - Check redirected to login
   - Check can't access search without login
   ```

5. **Test Password Reset**
   ```
   - Click "Forgot Password"
   - Enter email
   - Check email received
   - Click reset link
   - Set new password
   - Login with new password
   ```

6. **Test Admin Notification**
   ```
   - Register new user
   - Check Chris receives email
   - Verify email has correct info
   ```

---

## 📧 Email Templates

### Verification Email
```
Subject: Verify Your Promethean Light Email

Welcome, [Name]!

Please verify your email by clicking:
[Verification Link]

This link expires in 24 hours.
```

### Password Reset Email
```
Subject: Reset Your Promethean Light Password

Hi [Name],

Click to reset your password:
[Reset Link]

This link expires in 1 hour.
```

### Admin Notification Email
```
Subject: New User Registration: [Name]

New user registered:
Name: [Full Name]
Email: [Email]
Time: [Timestamp]
Status: Pending email verification

User auto-approved.
```

### Welcome Email
```
Subject: Welcome to Promethean Light!

You're all set, [Name]!

Your email is verified. Login at:
[Login Link]

Quick Start:
- Search for documents
- View recent items
- Browse by tags
```

---

## 🐛 Troubleshooting

### "Email not sending"

**Check:**
1. SMTP credentials correct in `.env`
2. App password (not regular password)
3. Firewall allows port 587
4. Run test:
   ```python
   from mydata.email_service import EmailService
   service = EmailService()
   service.send_email("test@vysusgroup.com", "Test", "Test body")
   ```

### "Can't register"

**Check:**
1. Email is @vysusgroup.com
2. Password is 8+ characters
3. Database tables created
4. API server running

### "Token expired"

**Solution:**
- Verification: Request new verification email
- Password reset: Request new reset link
- Session: Login again

### "Admin not receiving emails"

**Check:**
1. `ADMIN_EMAIL` set correctly in `.env`
2. Chris's email not in spam
3. SMTP sending working

---

## 🚀 Go-Live Checklist

- [ ] Install required packages (passlib, pyjwt)
- [ ] Create `.env` file with SMTP settings
- [ ] Get Office 365 app password
- [ ] Update database schema (create auth tables)
- [ ] Integrate auth routes into api.py
- [ ] Protect existing API endpoints
- [ ] Test registration flow
- [ ] Test email verification
- [ ] Test login/logout
- [ ] Test password reset
- [ ] Test admin notifications
- [ ] Share URL with team
- [ ] Send team instructions

---

## 📖 Team Instructions (Email Template)

```
Subject: Promethean Light - Registration Instructions

Team,

Promethean Light Knowledge Base is now available with user authentication!

GETTING STARTED:
1. Visit: http://10.210.250.5:8000
2. Click "Register"
3. Use your @vysusgroup.com email
4. Create a password (min 8 characters)
5. Check your email for verification link
6. Click verification link
7. Login and start searching!

FEATURES:
- Smart search across emails and documents
- Recent documents
- Browse by tags
- Topic clusters

NEED HELP?
- Forgot password? Click "Forgot Password" on login page
- Didn't receive verification email? Check spam folder
- Issues? Contact Chris

Best,
Chris
```

---

## 💡 Future Enhancements

### Optional Features You Can Add Later

1. **Two-Factor Authentication (2FA)**
   - SMS or authenticator app
   - Extra security layer

2. **User Admin Panel**
   - Manage users
   - View login history
   - Deactivate accounts

3. **API Keys**
   - Programmatic access
   - For integrations

4. **Activity Logging**
   - Search history
   - Access logs
   - Analytics

5. **Team/Group Management**
   - Organize by department
   - Permission levels
   - Shared folders

6. **Single Sign-On (SSO)**
   - Integrate with Azure AD
   - Microsoft Account login
   - No separate password

---

## 🎉 What You Have Now

**URLs:**
```
Login/Register: http://10.210.250.5:8000
Search (after login): http://10.210.250.5:8000/search
```

**Features:**
- ✓ Beautiful web interface
- ✓ User registration (@vysusgroup.com only)
- ✓ Email verification
- ✓ Secure login/logout
- ✓ Password reset
- ✓ Admin notifications
- ✓ Auto-approval
- ✓ Session management
- ✓ Protected API endpoints

**What Users See:**
1. Professional login page
2. Register with company email
3. Verify email (check inbox)
4. Login
5. Search interface with results
6. Recent documents
7. Tags and clusters

**What You (Chris) See:**
- Email notification for each new user
- User details (name, email, time)
- Auto-approval confirmation

---

## 📞 Support

**Setup Issues:**
- Check `.env` file configuration
- Verify SMTP credentials
- Ensure database tables created
- Check firewall allows port 587

**User Issues:**
- Password reset available
- Verification email resend available
- Admin can manually verify users if needed

**Technical Support:**
- All code is in `mydata/auth_*` files
- Email templates in `email_service.py`
- Web UI in `mydata/static/`

---

**Status:** Ready to deploy after configuration!
**Estimated Setup Time:** 15-20 minutes
**User Registration:** Self-service with email verification
**Admin Involvement:** Receive notifications, no approval needed

🚀 **Let's get this live!**
