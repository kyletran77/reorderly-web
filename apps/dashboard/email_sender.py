"""
Email sender for Purchase Orders.
Sends PO emails to suppliers via SMTP.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_po_email(po) -> bool:
    """Send a PO email to the supplier. Returns True on success."""
    smtp_host = os.environ.get('SMTP_HOST', '')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASS', '')
    from_email = os.environ.get('FROM_EMAIL', smtp_user)

    if not all([smtp_host, smtp_user, smtp_pass]):
        return False

    subject = f"Purchase Order {po.po_number} — {po.store.shop_name or po.store.shop_domain}"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = po.supplier.email
    if smtp_user and smtp_user != po.supplier.email:
        msg['Cc'] = smtp_user  # BCC a copy to the merchant

    # Plain text body
    plain_body = po.email_body or f"Please see purchase order {po.po_number} attached."
    msg.attach(MIMEText(plain_body, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            recipients = [po.supplier.email]
            if smtp_user and smtp_user != po.supplier.email:
                recipients.append(smtp_user)
            server.sendmail(from_email, recipients, msg.as_string())
        return True
    except Exception as e:
        return False
