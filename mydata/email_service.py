"""Email service for authentication notifications"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime


class EmailService:
    """Handle email sending via Office 365 SMTP"""

    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.office365.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.admin_email = os.getenv("ADMIN_EMAIL", "chris.marinelli@vysusgroup.com")
        self.base_url = os.getenv("BASE_URL", "http://10.210.250.5:8000")

    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """Send an email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Add text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(self, to_email: str, full_name: str, verification_token: str) -> bool:
        """Send email verification link"""
        verification_link = f"{self.base_url}/verify?token={verification_token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f4f4f4; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #0066cc; color: white;
                          text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Promethean Light</h1>
                    <p>Knowledge Base Access</p>
                </div>
                <div class="content">
                    <h2>Welcome, {full_name}!</h2>
                    <p>Thank you for registering for Promethean Light Knowledge Base access.</p>
                    <p>Please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: white; padding: 10px;">{verification_link}</p>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Promethean Light Knowledge Base</p>
                    <p>Vysus Group Internal System</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Promethean Light, {full_name}!

        Please verify your email address by visiting this link:
        {verification_link}

        This link will expire in 24 hours.

        If you didn't request this, please ignore this email.

        --
        Promethean Light Knowledge Base
        Vysus Group Internal System
        """

        return self.send_email(
            to_email=to_email,
            subject="Verify Your Promethean Light Email",
            html_body=html_body,
            text_body=text_body
        )

    def send_password_reset_email(self, to_email: str, full_name: str, reset_token: str) -> bool:
        """Send password reset link"""
        reset_link = f"{self.base_url}/reset-password?token={reset_token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0066cc; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f4f4f4; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #cc0000; color: white;
                          text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Promethean Light</h1>
                    <p>Password Reset</p>
                </div>
                <div class="content">
                    <h2>Hi {full_name},</h2>
                    <p>We received a request to reset your password for Promethean Light.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: white; padding: 10px;">{reset_link}</p>
                    <p><strong>This link will expire in 1 hour.</strong></p>
                    <p><strong>If you didn't request this, please ignore this email.</strong> Your password will not be changed.</p>
                </div>
                <div class="footer">
                    <p>Promethean Light Knowledge Base</p>
                    <p>Vysus Group Internal System</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hi {full_name},

        We received a request to reset your password for Promethean Light.

        Reset your password by visiting this link:
        {reset_link}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email. Your password will not be changed.

        --
        Promethean Light Knowledge Base
        Vysus Group Internal System
        """

        return self.send_email(
            to_email=to_email,
            subject="Reset Your Promethean Light Password",
            html_body=html_body,
            text_body=text_body
        )

    def notify_admin_new_user(self, user_email: str, full_name: str) -> bool:
        """Notify admin (Chris) when a new user registers"""
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f4f4f4; }}
                .info {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #0066cc; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New User Registration</h1>
                    <p>Promethean Light Admin Notification</p>
                </div>
                <div class="content">
                    <h2>New User Registered</h2>
                    <p>A new user has registered for Promethean Light access:</p>
                    <div class="info">
                        <p><strong>Name:</strong> {full_name}</p>
                        <p><strong>Email:</strong> {user_email}</p>
                        <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                        <p><strong>Status:</strong> Pending email verification</p>
                    </div>
                    <p>The user has been automatically approved but must verify their email address before accessing the system.</p>
                    <p>You can manage users by accessing the admin panel at:</p>
                    <p><a href="{self.base_url}/admin">{self.base_url}/admin</a></p>
                </div>
                <div class="footer">
                    <p>Promethean Light Knowledge Base</p>
                    <p>Automated Admin Notification</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        NEW USER REGISTRATION - Promethean Light

        A new user has registered for Promethean Light access:

        Name: {full_name}
        Email: {user_email}
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        Status: Pending email verification

        The user has been automatically approved but must verify their email address before accessing the system.

        Manage users at: {self.base_url}/admin

        --
        Promethean Light Knowledge Base
        Automated Admin Notification
        """

        return self.send_email(
            to_email=self.admin_email,
            subject=f"New User Registration: {full_name}",
            html_body=html_body,
            text_body=text_body
        )

    def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        """Send welcome email after email verification"""
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f4f4f4; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #0066cc; color: white;
                          text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .tips {{ background: white; padding: 15px; margin: 15px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Promethean Light!</h1>
                </div>
                <div class="content">
                    <h2>You're All Set, {full_name}!</h2>
                    <p>Your email has been verified and you now have access to the Promethean Light Knowledge Base.</p>
                    <p style="text-align: center;">
                        <a href="{self.base_url}/login" class="button">Login Now</a>
                    </p>
                    <div class="tips">
                        <h3>Quick Start Guide:</h3>
                        <ul>
                            <li><strong>Search:</strong> Use the search bar to find documents, emails, and project information</li>
                            <li><strong>Recent:</strong> View recently added documents</li>
                            <li><strong>Tags:</strong> Browse by automatically generated tags</li>
                            <li><strong>Clusters:</strong> Explore documents organized by topic</li>
                        </ul>
                        <h3>Search Examples:</h3>
                        <ul>
                            <li>"India staff retention"</li>
                            <li>"Project pipeline"</li>
                            <li>"Alinta energy proposal"</li>
                        </ul>
                    </div>
                    <p>If you have any questions or issues, contact the administrator.</p>
                </div>
                <div class="footer">
                    <p>Promethean Light Knowledge Base</p>
                    <p>Vysus Group Internal System</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Promethean Light, {full_name}!

        Your email has been verified and you now have access to the Promethean Light Knowledge Base.

        Login at: {self.base_url}/login

        QUICK START:
        - Search: Find documents, emails, and project information
        - Recent: View recently added documents
        - Tags: Browse by automatically generated tags
        - Clusters: Explore documents organized by topic

        SEARCH EXAMPLES:
        - "India staff retention"
        - "Project pipeline"
        - "Alinta energy proposal"

        If you have any questions or issues, contact the administrator.

        --
        Promethean Light Knowledge Base
        Vysus Group Internal System
        """

        return self.send_email(
            to_email=to_email,
            subject="Welcome to Promethean Light!",
            html_body=html_body,
            text_body=text_body
        )
