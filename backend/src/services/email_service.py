"""Email service using Resend for sending transactional emails."""

import logging
from typing import Optional

import resend

from src.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails via Resend."""

    def __init__(self):
        """Initialize the email service with Resend API key."""
        if settings.resend_api_key:
            resend.api_key = settings.resend_api_key
        self.from_email = settings.email_from
        self.frontend_url = settings.frontend_url

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(settings.resend_api_key)

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """
        Send a password reset email to the user.

        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: Optional user display name

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured, cannot send password reset email")
            return False

        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        greeting = f"Hi {user_name}" if user_name else "Hi"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🔐 Password Reset Request</h1>
            </div>
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="font-size: 16px; margin-bottom: 20px;">{greeting},</p>
                <p style="font-size: 16px; margin-bottom: 20px;">
                    We received a request to reset your password for your AI Wealth Companion account.
                    Click the button below to create a new password:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white;
                              padding: 14px 30px;
                              text-decoration: none;
                              border-radius: 8px;
                              font-weight: 600;
                              display: inline-block;
                              font-size: 16px;">
                        Reset Password
                    </a>
                </div>
                <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
                    This link will expire in {settings.password_reset_expire_minutes} minutes.
                </p>
                <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
                    If you didn't request this password reset, you can safely ignore this email.
                    Your password will remain unchanged.
                </p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                    AI Wealth Companion - Your Personal Finance Assistant<br>
                    <a href="{self.frontend_url}" style="color: #667eea;">Visit our website</a>
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
{greeting},

We received a request to reset your password for your AI Wealth Companion account.

Click the link below to create a new password:
{reset_url}

This link will expire in {settings.password_reset_expire_minutes} minutes.

If you didn't request this password reset, you can safely ignore this email.
Your password will remain unchanged.

---
AI Wealth Companion - Your Personal Finance Assistant
        """

        try:
            response = resend.Emails.send({
                "from": self.from_email,
                "to": [to_email],
                "subject": "Reset Your Password - AI Wealth Companion",
                "html": html_content,
                "text": text_content,
            })
            logger.info(f"Password reset email sent to {to_email}, id: {response.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            return False

    async def send_password_changed_notification(
        self,
        to_email: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """
        Send a notification that the password was changed.

        Args:
            to_email: Recipient email address
            user_name: Optional user display name

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured")
            return False

        greeting = f"Hi {user_name}" if user_name else "Hi"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">✅ Password Changed Successfully</h1>
            </div>
            <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e5e7eb; border-top: none;">
                <p style="font-size: 16px; margin-bottom: 20px;">{greeting},</p>
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Your password for AI Wealth Companion has been successfully changed.
                </p>
                <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
                    If you did not make this change, please contact us immediately or reset your password.
                </p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                    AI Wealth Companion - Your Personal Finance Assistant
                </p>
            </div>
        </body>
        </html>
        """

        try:
            resend.Emails.send({
                "from": self.from_email,
                "to": [to_email],
                "subject": "Password Changed - AI Wealth Companion",
                "html": html_content,
            })
            return True
        except Exception as e:
            logger.error(f"Failed to send password changed notification: {e}")
            return False


# Singleton instance
email_service = EmailService()
