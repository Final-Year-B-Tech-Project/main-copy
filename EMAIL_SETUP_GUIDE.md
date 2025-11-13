# Email Configuration Setup Guide

## Quick Setup

1. **Create a `.env` file** in your project root directory
2. **Add the following email configuration:**

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to "Security"
3. Enable "2-Step Verification"

### Step 2: Generate App Password
1. In Google Account settings, go to "Security"
2. Under "2-Step Verification", click "App passwords"
3. Select "Mail" and "Windows Computer" (or Other)
4. Copy the generated 16-character password
5. Use this password in your `.env` file

### Step 3: Update .env File
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

## Other Email Providers

### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### Yahoo Mail
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-password
```

## Testing Your Configuration

Run the email test utility:

```bash
cd "Backend Files"
python app/email_test.py
```

This will:
- ✅ Check your configuration
- 📧 Send a test email to yourself
- 🔍 Show detailed error messages if something is wrong

## Common Issues & Solutions

### Issue: "Authentication failed"
**Solution:** Use App Password instead of regular password (for Gmail)

### Issue: "Connection refused"
**Solution:** Check MAIL_SERVER and MAIL_PORT settings

### Issue: "TLS/SSL error"
**Solution:** Verify MAIL_USE_TLS is set to 'true'

### Issue: "No emails being sent"
**Solution:** 
1. Check all environment variables are set
2. Run the email test utility
3. Check spam/junk folder

## Environment Variables Checklist

- [ ] `MAIL_SERVER` - SMTP server address
- [ ] `MAIL_PORT` - SMTP port (usually 587)
- [ ] `MAIL_USE_TLS` - Set to 'true'
- [ ] `MAIL_USERNAME` - Your email address
- [ ] `MAIL_PASSWORD` - Your email password/app password

## Security Best Practices

1. **Never commit `.env` file to version control**
2. **Use App Passwords instead of regular passwords**
3. **Enable 2-Factor Authentication on your email account**
4. **Regularly rotate your App Passwords**

## Email Features in AI Interview System

Once configured, the system will automatically send:

- 📧 **Shortlist notifications** to candidates
- 📅 **Interview scheduling** confirmations
- 📊 **Feedback emails** after interviews
- 🔄 **Bulk notifications** to multiple candidates
- 📝 **Registration invitations** for unregistered users

## Need Help?

If you're still having issues:

1. Run `python app/email_test.py` for detailed diagnostics
2. Check the console output for specific error messages
3. Verify your email provider's SMTP settings
4. Ensure your firewall isn't blocking SMTP connections