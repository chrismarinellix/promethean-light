# Promethean Light Authentication - Quick Start

## 🚀 Get Authentication Working in 20 Minutes

### Prerequisites
- Admin access to Microsoft 365 admin center OR
- Access to create app passwords

---

## Step 1: Enable SMTP AUTH (5 minutes)

### Option A: Use Microsoft 365 Admin Center
1. Go to https://admin.microsoft.com
2. Navigate to: **Users > Active users**
3. Select mailbox: **noreply@vysusgroup.com** (or create one)
4. Click: **Mail** tab
5. Click: **"Manage email apps"**
6. **Check:** "Authenticated SMTP"
7. Click: **"Save changes"**

### Option B: Use PowerShell (Faster)
```powershell
# Connect to Exchange Online
Install-Module -Name ExchangeOnlineManagement
Connect-ExchangeOnline -UserPrincipalName your-admin@vysusgroup.com

# Enable SMTP AUTH
Set-CASMailbox -Identity noreply@vysusgroup.com -SmtpClientAuthenticationDisabled $false

# Verify
Get-CASMailbox -Identity noreply@vysusgroup.com | Format-List SmtpClientAuthenticationDisabled
```

---

## Step 2: Get App Password (3 minutes)

1. Go to: https://account.microsoft.com/security
2. Click: **"Advanced security options"**
3. Under "App passwords": **"Create a new app password"**
4. **Copy** the password (e.g., `abcd efgh ijkl mnop`)
5. **Save it** - you won't see it again!

---

## Step 3: Install Authentication System (10 minutes)

### Run the installer:
```batch
cd "C:\Code\Promethian  Light"
INSTALL_AUTHENTICATION.bat
```

### You'll be prompted for:
1. **SMTP User:** noreply@vysusgroup.com
2. **SMTP Password:** [paste app password from Step 2]
3. **From Email:** noreply@vysusgroup.com
4. **Admin Email:** chris.marinelli@vysusgroup.com

The installer will:
- Install required packages
- Create database tables
- Configure email service
- Test email sending
- Show you the team URL

---

## Step 4: Test It! (2 minutes)

1. **Restart Promethean Light:**
   ```batch
   START_NETWORK_NOW.bat
   ```

2. **Visit:** http://10.210.250.5:8000

3. **Click "Register"** and fill in:
   - Name: Test User
   - Email: your-email@vysusgroup.com
   - Password: (min 8 chars)

4. **Check email:**
   - Verification email to user
   - **Admin notification to you!**

5. **Click verification link**

6. **Login** and search!

---

## ✅ Success Criteria

You'll know it's working when:
- ✓ You can visit http://10.210.250.5:8000
- ✓ Registration page loads
- ✓ Test user receives verification email
- ✓ **You receive admin notification email**
- ✓ User can verify and login
- ✓ Search page loads after login

---

## 🆘 Quick Troubleshooting

### "Email not sending"
- Check SMTP AUTH is enabled (Step 1)
- Verify app password is correct
- No spaces in app password in .env file

### "Authentication error"
- App password might be wrong
- Generate new app password
- Update .env file

### "Can't register"
- Must use @vysusgroup.com email
- Password must be 8+ characters
- Check database tables created

---

## 📧 What Gets Sent

When someone registers:
1. **User receives:** Verification email with link
2. **You (Chris) receive:** Notification with user details
3. **After verification:** User receives welcome email

---

## 🎯 What You Get

### User Features:
- Beautiful login/register page
- Email verification (required)
- Password reset via email
- Secure authentication

### Admin Features (You):
- Email notification for each new user
- Auto-approval (no manual approval needed)
- User details in notification email

### Security:
- Only @vysusgroup.com emails allowed
- Password hashing (bcrypt)
- JWT tokens
- Session management

---

## 📱 Share with Team

After setup, share this URL:
```
http://10.210.250.5:8000
```

**Email template:**
```
Team,

Promethean Light is now live with user accounts!

1. Visit: http://10.210.250.5:8000
2. Click "Register"
3. Use your @vysusgroup.com email
4. Check email for verification link
5. Login and start searching!

- Chris
```

---

## 📖 Full Documentation

- **SMTP Setup:** See `ENABLE_OFFICE365_SMTP.md`
- **Complete Guide:** See `AUTHENTICATION_SETUP_GUIDE.md`
- **Network Server:** See `LAPTOP_SERVER_SETUP.md`

---

## ⚡ TL;DR Command List

```batch
# 1. Enable SMTP AUTH (PowerShell)
Set-CASMailbox -Identity noreply@vysusgroup.com -SmtpClientAuthenticationDisabled $false

# 2. Get app password from https://account.microsoft.com/security

# 3. Install authentication
cd "C:\Code\Promethian  Light"
INSTALL_AUTHENTICATION.bat

# 4. Restart server
START_NETWORK_NOW.bat

# 5. Visit
# http://10.210.250.5:8000
```

---

**Total Time:** ~20 minutes
**Difficulty:** Easy (with admin access)
**Result:** Full authentication system with email integration!
