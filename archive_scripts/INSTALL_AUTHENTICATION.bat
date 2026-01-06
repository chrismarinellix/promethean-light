@echo off
REM Install authentication system for Promethean Light

echo ========================================
echo PROMETHEAN LIGHT
echo Authentication System Installation
echo ========================================
echo.

echo This will install the authentication system with:
echo   - User registration and login
echo   - Email verification
echo   - Password reset
echo   - Office 365 email integration
echo   - Auto-approval for @vysusgroup.com emails
echo.
pause

echo.
echo [Step 1/5] Installing required Python packages...
pip install passlib[bcrypt] pyjwt python-jose[cryptography]

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages
    pause
    exit /b 1
)

echo [OK] Packages installed
echo.

echo [Step 2/5] Creating database tables...
python -c "from mydata.database import Database; from mydata.auth_models import User, UserSession, LoginAttempt; from sqlmodel import SQLModel; db = Database(); SQLModel.metadata.create_all(db.engine); print('Tables created successfully')"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to create database tables
    pause
    exit /b 1
)

echo [OK] Database tables created
echo.

echo [Step 3/5] Creating configuration file...
echo Please provide the following information:
echo.

set /p SMTP_USER="Office 365 Email (e.g., promethean@vysusgroup.com): "
set /p SMTP_PASSWORD="Office 365 App Password (from https://account.microsoft.com/security): "
set /p FROM_EMAIL="From Email Address (e.g., noreply@vysusgroup.com): "
set /p ADMIN_EMAIL="Admin Email (e.g., chris.marinelli@vysusgroup.com): "

echo.
echo Creating .env file...

(
echo # Promethean Light Authentication Configuration
echo # Generated: %date% %time%
echo.
echo # Email Configuration ^(Office 365^)
echo SMTP_SERVER=smtp.office365.com
echo SMTP_PORT=587
echo SMTP_USER=%SMTP_USER%
echo SMTP_PASSWORD=%SMTP_PASSWORD%
echo FROM_EMAIL=%FROM_EMAIL%
echo ADMIN_EMAIL=%ADMIN_EMAIL%
echo.
echo # Base URL for links in emails
echo BASE_URL=http://10.210.250.5:8000
echo.
echo # API Configuration
echo API_HOST=0.0.0.0
echo API_PORT=8000
) > .env

echo [OK] Configuration file created: .env
echo.

echo [Step 4/5] Testing email configuration...
python -c "from mydata.email_service import EmailService; import sys; service = EmailService(); success = service.send_email('%ADMIN_EMAIL%', 'Test Email', '<h1>Test</h1>', 'Test'); sys.exit(0 if success else 1)"

if %errorlevel% neq 0 (
    echo [WARNING] Email test failed - check your credentials
    echo You can continue, but emails won't be sent until this is fixed
    pause
) else (
    echo [OK] Email test successful - check %ADMIN_EMAIL% for test email
)

echo.

echo [Step 5/5] Installation Summary
echo.
echo ========================================
echo INSTALLATION COMPLETE
echo ========================================
echo.
echo What's been installed:
echo   - User authentication system
echo   - Login/Register web interface
echo   - Email verification
echo   - Password reset
echo   - Office 365 email integration
echo.
echo Configuration:
echo   - SMTP User: %SMTP_USER%
echo   - From Email: %FROM_EMAIL%
echo   - Admin Email: %ADMIN_EMAIL%
echo   - Config File: .env
echo.
echo Next Steps:
echo   1. Restart Promethean Light server
echo   2. Visit http://10.210.250.5:8000
echo   3. Test registration with @vysusgroup.com email
echo   4. Check email for verification link
echo   5. Login and start using!
echo.
echo Team Access URL:
echo   http://10.210.250.5:8000
echo.
echo Documentation:
echo   See AUTHENTICATION_SETUP_GUIDE.md for complete details
echo.
pause
