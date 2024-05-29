import os
import ssl
import sendgrid
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from sendgrid.helpers.mail import Mail
import logging
import sys
import publisher_mailing

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the level of this logger.
# DEBUG, INFO, WARNING, ERROR, CRITICAL can be used depending on the granularity of log you want.
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
s_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
s_handler.setLevel(logging.DEBUG)  # Set level to DEBUG

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
s_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
s_handler.setFormatter(s_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(s_handler)


# Create a default SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Rest of your code remains the same
# from address we pass to our Mail object, edit with your name
FROM_EMAIL = 'gdt.intratech@ehb.be'


def Send_email(inhoud):
    try:
        logger.info("Sending email...")
        sg = sendgrid.SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(inhoud)
        code, body, headers = response.status_code, response.body, response.headers
        # print(f"Response code: {code}")
        # print(f"Response headers: {headers}")
        # print(f"Response body: {body}")
        logger.info("Messages Sent!")
        logsendmail = "Mail send"
        publisher_mailing.sendLogsToMonitoring("Mail has been send", logsendmail, False)
    except Exception as e:
        print("Error: {0}".format(e))
        loggerpub = (f"Error: {0}".format(e))
        publisher_mailing.sendLogsToMonitoring("Error sending mail", loggerpub, False)


def send_welcome_mail(email, name):
    logger.info("Entered welcome mail function")
    # update to your dynamic template id from the UI
    TEMPLATE_ID = 'd-6a0bfab49443471a91a76608083db6eb'
    # list of emails and preheader names, update with yours
    TO_EMAILS = [(email, name)]
    # create Mail object and populate
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS)
    # pass custom values for our HTML placeholders
    message.dynamic_template_data = {
        'name': name
    }
    message.template_id = TEMPLATE_ID
    Send_email(message)


def send_mail_service_down(name, status, timestamp):
    # update to your dynamic template id from the UI
    TEMPLATE_ID = 'd-045e38832342427eb14fa50e326a1d4c'
    # list of emails and preheader names, update with yours
    TO_EMAILS = [('intratechconsulting1@gmail.com', 'dev')]
    # create Mail object and populate
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS)
    # pass custom values for our HTML placeholders
    message.dynamic_template_data = {
        'service': name,
        'status' : status,
        'timetitle' : 'Downtime',
        'time' : timestamp
    }
    message.template_id = TEMPLATE_ID
    Send_email(message)


def send_mail_service_up(name, status, timestamp):
    # update to your dynamic template id from the UI
    TEMPLATE_ID = 'd-045e38832342427eb14fa50e326a1d4c'
    # list of emails and preheader names, update with yours
    TO_EMAILS = [('intratechconsulting1@gmail.com', 'dev')]
    # create Mail object and populate
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS)
    # pass custom values for our HTML placeholders
    message.dynamic_template_data = {
        'service': name,
        'status' : status,
        'timetitle' : 'Backup',
        'time' : timestamp
    }
    message.template_id = TEMPLATE_ID
    Send_email(message)

def send_invoice_mail(email,filename,invoice):
    # update to your dynamic template id from the UI
    TEMPLATE_ID = 'd-221bd5139ae34c3c99248f4fd456aabf'
    # list of emails and preheader names, update with yours
    TO_EMAILS = [(email, 'company')]
    # create Mail object and populate
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS)
    attachedFile = Attachment(
        FileContent(invoice),
        FileName(filename + '.pdf'),
        FileType('application/pdf'),
        Disposition('attachment')
    )
    message.attachment = attachedFile
    message.template_id = TEMPLATE_ID
    Send_email(message)


if __name__ == "__main__":
    send_welcome_mail()
