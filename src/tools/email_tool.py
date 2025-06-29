"""
Email sending tool using Gmail SMTP.
"""
import smtplib
import ssl
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from agents import function_tool
from config.settings import settings



@function_tool
def send_recommendation_email(recommendation: str, recommendation_type: str = "recommendation") -> str:
    """
    Send a recommendation email via Gmail SMTP.
    
    Args:
        recommendation: The formatted recommendation content
        recommendation_type: Type of recommendation (restaurant, poi, movie)
    
    Returns:
        Success or error message
    """
    try:
        # Create message with proper MIME structure for embedded images
        message = MIMEMultipart("related")
        message["Subject"] = f"🌀 Randy's {recommendation_type.title()} Suggestion - {datetime.now().strftime('%B %d')}"
        message["From"] = settings.GMAIL_USERNAME
        message["To"] = settings.RECIPIENT_EMAIL
        
        # Create the plain text email body (fallback for non-HTML email clients)
        email_body = f"""{recommendation}

Cheers,
Randy 🌀

---
This is an automated recommendation from your friendly Randy agent.
"""
        
        # Check for Randy logo
        logo_embedded = False
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "images", "randy_logo.png")
        logo_data = None
        
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                logo_embedded = True
            except Exception as e:
                print(f"Warning: Could not read logo: {e}")
        
        # Create HTML version with or without logo
        logo_html = ""
        if logo_embedded:
            logo_html = '''
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="cid:randy_logo" alt="Randy Logo" style="width: 100px; height: 100px; border-radius: 50%; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            </div>
            '''
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            {logo_html}
            
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4a90e2; margin-bottom: 5px; font-size: 28px;">Randy's Recommendations</h1>
                <p style="color: #666; font-style: italic; margin: 0;">Your weekly dose of spontaneity</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #4a90e2; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
              {recommendation}
            </div>
            
            <p style="margin-top: 30px; text-align: center;">Cheers,<br><strong>Randy 🌀</strong></p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 40px 0;">
            <div style="text-align: center;">
                <p style="font-size: 12px; color: #666; margin: 0;">This is an automated recommendation from your friendly Randy agent.</p>
                <p style="font-size: 11px; color: #999; margin: 5px 0 0 0;">Bringing spontaneity to your week, one recommendation at a time.</p>
            </div>
          </body>
        </html>
        """
        
        # Create multipart message structure
        msg_alternative = MIMEMultipart("alternative")
        
        # Create text and HTML parts
        text_part = MIMEText(email_body, "plain")
        html_part = MIMEText(html_body, "html")
        
        # Add parts to alternative container
        msg_alternative.attach(text_part)
        msg_alternative.attach(html_part)
        
        # Add the alternative container to the main message FIRST
        message.attach(msg_alternative)
        
        # Then add the logo image if available (with proper headers to prevent attachment display)
        if logo_embedded and logo_data:
            try:
                logo_image = MIMEImage(logo_data)
                logo_image.add_header('Content-ID', '<randy_logo>')
                logo_image.add_header('Content-Disposition', 'inline')
                # Remove filename to prevent showing as attachment
                logo_image.set_param('name', '')
                message.attach(logo_image)
            except Exception as e:
                print(f"Warning: Could not embed logo: {e}")
                logo_embedded = False
        
        # Create SMTP session
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(settings.GMAIL_USERNAME, settings.GMAIL_APP_PASSWORD)
            text = message.as_string()
            server.sendmail(settings.GMAIL_USERNAME, settings.RECIPIENT_EMAIL, text)
        
        logo_status = "with logo" if logo_embedded else "without logo (logo file not found)"
        return f"✅ Email sent successfully to {settings.RECIPIENT_EMAIL} {logo_status}!"
        
    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Please check your Gmail username and app password."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error occurred: {str(e)}"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}" 