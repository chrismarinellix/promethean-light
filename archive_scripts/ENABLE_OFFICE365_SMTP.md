# Enable Office 365 SMTP for Promethean Light

## 📧 What You Need

For Promethean Light to send emails (verification, password reset, admin notifications), you need to enable SMTP AUTH on an Office 365 mailbox.

---

## ⚠️ Important: SMTP AUTH is Often Disabled

**By default, SMTP AUTH is disabled in Office 365 organizations** due to security defaults.

You need to:
1. Enable SMTP AUTH for a specific mailbox
2. Create an app password for that mailbox
3. Use those credentials in Promethean Light

---

## 🔧 Step-by-Step Setup

### Step 1: Choose Email Account

Decide which Office 365 mailbox will send emails:

**Option A: Use existing mailbox** (e.g., chris.marinelli@vysusgroup.com)
- Pros: Simple, no new account needed
- Cons: Emails come from your personal mailbox

**Option B: Create dedicated mailbox** (e.g., noreply@vysusgroup.com)
- Pros: Professional, separate from personal email
- Cons: Requires mailbox license

**Recommendation:** Use dedicated mailbox (noreply@vysusgroup.com or promethean@vysusgroup.com)

---

### Step 2: Enable SMTP AUTH for the Mailbox

#### Method A: Using Microsoft 365 Admin Center (GUI)

1. **Go to:** https://admin.microsoft.com
2. **Navigate to:** Users > Active users
3. **Select:** The mailbox (e.g., noreply@vysusgroup.com)
4. **Click:** Mail tab
5. **Click:** "Manage email apps"
6. **Check:** "Authenticated SMTP" checkbox
7. **Click:** "Save changes"

#### Method B: Using PowerShell (Faster)

1. **Connect to Exchange Online:**
   ```powershell
   Install-Module -Name ExchangeOnlineManagement
   Connect-ExchangeOnline -UserPrincipalName admin@vysusgroup.com
   ```

2. **Enable SMTP AUTH for mailbox:**
   ```powershell
   Set-CASMailbox -Identity noreply@vysusgroup.com -SmtpClientAuthenticationDisabled $false
   ```

3. **Verify it worked:**
   ```powershell
   Get-CASMailbox -Identity noreply@vysusgroup.com | Format-List SmtpClientAuthenticationDisabled
   ```
   Should show: `SmtpClientAuthenticationDisabled : False`

---

### Step 3: Create App Password

**IMPORTANT:** Don't use your regular password! Create an app-specific password.

1. **Sign in to:** https://account.microsoft.com/security
2. **Navigate to:** Security > Advanced security options
3. **Under "App passwords":** Click "Create a new app password"
4. **Copy the password:** You'll use this in the .env file
5. **Save it:** You won't be able to see it again

**Example app password:** `abcd efgh ijkl mnop`

---

### Step 4: Configure Promethean Light

Create or update `.env` file in `C:\Code\Promethian Light\`:

```env
# Email Configuration (Office 365)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=noreply@vysusgroup.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=noreply@vysusgroup.com
ADMIN_EMAIL=chris.marinelli@vysusgroup.com

# Base URL for links in emails
BASE_URL=http://10.210.250.5:8000
```

**Replace:**
- `noreply@vysusgroup.com` with your chosen mailbox
- `abcd efgh ijkl mnop` with your app password
- `chris.marinelli@vysusgroup.com` with your admin email

---

### Step 5: Test Email Sending

```python
python -c "from mydata.email_service import EmailService; service = EmailService(); print('Sending test...'); success = service.send_email('chris.marinelli@vysusgroup.com', 'Test', '<h1>Test Email</h1>', 'Test'); print('Success!' if success else 'Failed')"
```

**If successful:** Check your inbox for test email

**If failed:** Check:
- SMTP AUTH is enabled for the mailbox
- App password is correct (no spaces in .env)
- Firewall allows port 587

---

## 🔍 Troubleshooting

### Error: "Username and Password not accepted"

**Solution:**
1. Verify SMTP AUTH is enabled:
   ```powershell
   Get-CASMailbox -Identity noreply@vysusgroup.com | Format-List SmtpClientAuthenticationDisabled
   ```
   Should be `False`

2. Verify app password is correct
3. Try generating new app password

### Error: "Security defaults prevent SMTP AUTH"

**Solution:**
Your organization has security defaults enabled. You need to either:
1. Disable security defaults (not recommended)
2. Use a different authentication method
3. Contact your IT admin

To check security defaults:
1. Go to https://portal.azure.com
2. Navigate to Azure Active Directory
3. Click Properties
4. Check "Security defaults" status

### Error: "Connection timeout"

**Solution:**
- Firewall is blocking port 587
- Add firewall exception:
  ```powershell
  New-NetFirewallRule -DisplayName "SMTP Outbound" -Direction Outbound -Action Allow -Protocol TCP -RemotePort 587
  ```

### Error: "Authentication policy prevents SMTP"

**Solution:**
Your organization has disabled basic auth globally. Contact IT admin to:
1. Create exception for SMTP AUTH
2. Or use Modern Auth/OAuth (more complex)

---

## 📋 Quick Setup Checklist

- [ ] Choose email account (noreply@vysusgroup.com recommended)
- [ ] Enable SMTP AUTH for that mailbox
- [ ] Verify SMTP AUTH is enabled (PowerShell check)
- [ ] Create app password for the mailbox
- [ ] Save app password securely
- [ ] Update .env file with credentials
- [ ] Test email sending
- [ ] Check inbox for test email
- [ ] Install authentication system

---

## 🎯 Recommended Configuration

```env
# Recommended for Promethean Light
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=promethean@vysusgroup.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=Promethean Light <promethean@vysusgroup.com>
ADMIN_EMAIL=chris.marinelli@vysusgroup.com
BASE_URL=http://10.210.250.5:8000
```

This sends emails from a dedicated "Promethean Light" mailbox, keeping them separate from personal email.

---

## 🔐 Security Notes

### App Passwords
- More secure than regular passwords
- Can be revoked without changing account password
- Unique per application
- No spaces when entering in .env

### SMTP AUTH Security
- Only enable for mailboxes that need it
- Use app passwords, not regular passwords
- Monitor for unauthorized use
- Disable if not needed

### Alternative: Modern Auth (OAuth)
For better security, you can use OAuth instead of basic auth:
- More secure (no password storage)
- Supports MFA
- Token-based authentication
- Requires more complex setup

**For now, app passwords are simpler and sufficient for internal use.**

---

## 📧 Email Types Sent by Promethean Light

1. **Verification Email**
   - Sent to: New user
   - When: User registers
   - Contains: Verification link (24hr expiry)

2. **Welcome Email**
   - Sent to: User
   - When: Email verified
   - Contains: Login link, quick start guide

3. **Password Reset Email**
   - Sent to: User
   - When: User requests reset
   - Contains: Reset link (1hr expiry)

4. **Admin Notification**
   - Sent to: You (Chris)
   - When: Someone registers
   - Contains: User name, email, timestamp

---

## ✅ Verification Commands

### Check SMTP AUTH Status
```powershell
Connect-ExchangeOnline
Get-CASMailbox -Identity noreply@vysusgroup.com | Format-List SmtpClientAuthenticationDisabled
```

### Enable SMTP AUTH
```powershell
Set-CASMailbox -Identity noreply@vysusgroup.com -SmtpClientAuthenticationDisabled $false
```

### Check All Mailboxes with SMTP AUTH Enabled
```powershell
$Users = Get-CASMailbox -ResultSize unlimited
$Users | where {$_.SmtpClientAuthenticationDisabled -eq $false} | Select-Object DisplayName, PrimarySmtpAddress
```

---

## 🚀 Next Steps

After configuring Office 365 SMTP:

1. **Test email sending** (above)
2. **Run installation:** `INSTALL_AUTHENTICATION.bat`
3. **Restart server**
4. **Test registration** with your email
5. **Check you receive admin notification**

---

## 💡 Alternative SMTP Providers

If Office 365 doesn't work, you can use:

### SendGrid (Free tier: 100 emails/day)
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Gmail (App password required)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Mailgun
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

**Recommendation:** Stick with Office 365 for consistency with your organization.

---

## 📞 Need Help?

**Error messages:** Check "Troubleshooting" section above

**PowerShell access issues:** Contact IT admin

**SMTP blocked by organization:** Contact IT admin to request exception

**General setup:** See AUTHENTICATION_SETUP_GUIDE.md

---

**Status:** Office 365 SMTP configuration required before authentication system can send emails
**Time:** 10-15 minutes
**Difficulty:** Intermediate (requires admin access or IT support)
