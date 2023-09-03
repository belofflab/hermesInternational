import imaplib
import email
import ssl
from email.header import decode_header

from django.conf import settings

def decode_subject(header):
    value, charset = decode_header(header)[0]
    if charset:
        return value.decode(charset)
    else:
        return value

def get_email_list(mailbox, criteria='ALL'):
    result, data = mailbox.search(None, criteria)
    email_list = data[0].split()
    return email_list

def fetch_email_data(mailbox, email_id):
    result, message_data = mailbox.fetch(email_id, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
    raw_email = message_data[0][1]
    msg = email.message_from_bytes(raw_email)
    subject = decode_subject(msg["Subject"])
    sender = msg["From"]
    date = msg["Date"]
    return {
        "Subject": subject,
        "From": sender,
        "Date": date,
        "ID": email_id,
    }

def get_email():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST, 993, ssl_context=context)

    mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    mail.select('INBOX')

    email_list = []
    email_ids = get_email_list(mail)
    for email_id in email_ids:
        email_data = fetch_email_data(mail, email_id)
        email_list.append(email_data)

    mail.logout()

    return email_list