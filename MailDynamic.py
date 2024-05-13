import os
import ssl
import sendgrid
from sendgrid.helpers.mail import Mail

# Create a default SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Rest of your code remains the same
# from address we pass to our Mail object, edit with your name
FROM_EMAIL = 'intratechconsulting@outlook.com'


def Send_email(inhoud):
    try:
        sg = sendgrid.SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(inhoud)
        code, body, headers = response.status_code, response.body, response.headers
        # print(f"Response code: {code}")
        # print(f"Response headers: {headers}")
        # print(f"Response body: {body}")
        print("Messages Sent!")
    except Exception as e:
        print("Error: {0}".format(e))
        

def send_welcome_mail(email, name):
    # update to your dynamic template id from the UI
    TEMPLATE_ID = 'd-9637d65d68984cfc8cccf34f2ddfa6bb'
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
    TEMPLATE_ID = 'd-1664eba4bf2c4367a0282be35e5045d5'
    # list of emails and preheader names, update with yours
    TO_EMAILS = [('intratechconsulting@outlook.com', 'dev')]
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
    TEMPLATE_ID = 'd-1664eba4bf2c4367a0282be35e5045d5'
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


if __name__ == "__main__":
    send_welcome_mail()
