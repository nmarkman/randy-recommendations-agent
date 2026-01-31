"""
Email sending tool using Gmail SMTP.
"""
import smtplib
import ssl
import os
import re
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from agents import function_tool
from config.settings import settings

logger = logging.getLogger('Randy.EmailTool')

# Pattern to match Google Places photo URLs in HTML
GOOGLE_PLACES_PHOTO_PATTERN = re.compile(
    r'<img\s+[^>]*src=["\']'
    r'(https://maps\.googleapis\.com/maps/api/place/photo\?[^"\']+)'
    r'["\'][^>]*>',
    re.IGNORECASE
)


def _ensure_api_key_in_url(url: str) -> str:
    """
    Ensure Google Places photo URLs have the API key.

    The LLM agent sometimes strips API keys from URLs for security.
    This function re-adds the key if missing.

    Args:
        url: The Google Places photo URL

    Returns:
        URL with API key included
    """
    if 'maps.googleapis.com/maps/api/place/photo' in url:
        if 'key=' not in url:
            # Add the API key
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}key={settings.GOOGLE_PLACES_API_KEY}"
            logger.debug("Added missing API key to Google Places photo URL")
    return url


def _download_image(url: str, timeout: int = 10) -> bytes | None:
    """
    Download an image from a URL, following redirects.

    Args:
        url: The image URL to download
        timeout: Request timeout in seconds

    Returns:
        Image data as bytes, or None if download failed
    """
    try:
        # Ensure Google Places URLs have the API key
        url = _ensure_api_key_in_url(url)

        logger.debug(f"Downloading image from: {url[:100]}...")
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Verify we got image data
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type.lower():
            logger.warning(f"URL did not return image data: {content_type}")
            return None

        logger.debug(f"Successfully downloaded image ({len(response.content)} bytes)")
        return response.content
    except Exception as e:
        logger.warning(f"Failed to download image: {e}")
        return None


def _process_google_places_images(html_content: str) -> tuple[str, list[tuple[str, bytes]]]:
    """
    Find Google Places photo URLs in HTML, download them, and replace with CID references.

    Args:
        html_content: The HTML content to process

    Returns:
        Tuple of (modified_html, list of (cid, image_data) tuples)
    """
    images_to_embed = []
    modified_html = html_content

    # Find all Google Places photo URLs
    matches = GOOGLE_PLACES_PHOTO_PATTERN.findall(html_content)

    for i, url in enumerate(matches):
        logger.info(f"Found Google Places photo URL, attempting to download...")
        image_data = _download_image(url)

        if image_data:
            # Generate a unique CID for this image
            cid = f"places_photo_{i}"
            images_to_embed.append((cid, image_data))

            # Replace the URL in the HTML with the CID reference
            # We need to replace the entire img tag to maintain attributes
            old_tag_pattern = re.compile(
                r'<img\s+([^>]*)src=["\']' + re.escape(url) + r'["\']([^>]*)>',
                re.IGNORECASE
            )
            new_tag = f'<img \\1src="cid:{cid}"\\2>'
            modified_html = old_tag_pattern.sub(new_tag, modified_html)

            logger.info(f"Successfully processed Google Places image, will embed with CID: {cid}")
        else:
            # If download failed, remove the broken image tag or replace with placeholder
            logger.warning("Could not download Google Places image, removing from email")
            # Remove the img tag entirely to avoid broken image
            old_tag_pattern = re.compile(
                r'<img\s+[^>]*src=["\']' + re.escape(url) + r'["\'][^>]*>',
                re.IGNORECASE
            )
            modified_html = old_tag_pattern.sub('', modified_html)

    return modified_html, images_to_embed

def _send_smtp_email(message: MIMEMultipart, recipient_email: str):
    """
    Send email via SMTP.
    
    Args:
        message: Prepared MIME message
        recipient_email: Recipient email address
    """
    logger.info(f"Attempting to send email to {recipient_email}")
    
    # Create SMTP session
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(settings.GMAIL_USERNAME, settings.GMAIL_APP_PASSWORD)
        text = message.as_string()
        server.sendmail(settings.GMAIL_USERNAME, recipient_email, text)
    
    logger.info(f"Email successfully sent to {recipient_email}")

def _prepare_email_message(recommendation: str, recommendation_type: str) -> tuple:
    """
    Prepare the email message with all attachments and content.

    Args:
        recommendation: The formatted recommendation content
        recommendation_type: Type of recommendation

    Returns:
        Tuple of (message, logo_embedded_status)
    """
    logger.debug("Preparing email message with attachments")

    # Process Google Places images - download and prepare for embedding
    processed_recommendation, places_images = _process_google_places_images(recommendation)
    logger.info(f"Processed {len(places_images)} Google Places images for embedding")
    
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
            logger.debug("Successfully loaded Randy logo for embedding")
        except Exception as e:
            logger.warning(f"Could not read logo: {e}")
    else:
        logger.warning(f"Logo file not found at {logo_path}")
    
    # Create HTML version with or without logo
    logo_html = ""
    if logo_embedded:
        logo_html = '''
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="cid:randy_logo" alt="Randy Logo" style="width: 100px; height: 100px; border-radius: 50%; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        </div>
        '''
    
    # Use processed_recommendation (with CID references) in HTML
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        {logo_html}

        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #4a90e2; margin-bottom: 5px; font-size: 28px;">Randy's Recommendations</h1>
            <p style="color: #666; font-style: italic; margin: 0;">Your weekly dose of spontaneity</p>
        </div>

        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #4a90e2; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
          {processed_recommendation}
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
            logger.debug("Successfully embedded logo in email")
        except Exception as e:
            logger.warning(f"Could not embed logo: {e}")
            logo_embedded = False

    # Embed Google Places images
    for cid, image_data in places_images:
        try:
            places_image = MIMEImage(image_data)
            places_image.add_header('Content-ID', f'<{cid}>')
            places_image.add_header('Content-Disposition', 'inline')
            places_image.set_param('name', '')
            message.attach(places_image)
            logger.debug(f"Successfully embedded Places image with CID: {cid}")
        except Exception as e:
            logger.warning(f"Could not embed Places image {cid}: {e}")

    return message, logo_embedded

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
        logger.info(f"Starting email send process for {recommendation_type} recommendation")
        
        # Prepare the email message
        message, logo_embedded = _prepare_email_message(recommendation, recommendation_type)
        
        # Send the email
        _send_smtp_email(message, settings.RECIPIENT_EMAIL)
        
        # Success message
        logo_status = "with logo" if logo_embedded else "without logo (logo file not found)"
        success_msg = f"✅ Email sent successfully to {settings.RECIPIENT_EMAIL} {logo_status}!"
        logger.info(success_msg)
        return success_msg
        
    except Exception as e:
        error_msg = f"❌ Failed to send email: {str(e)}"
        logger.error(f"Email error: {e}")
        return error_msg 