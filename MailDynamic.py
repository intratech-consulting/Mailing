import os
import ssl
import sendgrid
from sendgrid.helpers.mail import Mail

# Create a default SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Rest of your code remains the same
# from address we pass to our Mail object, edit with your name
FROM_EMAIL = 'mats.deraymaeker@student.ehb.be'

def Send_email(inhoud):
    try:
        sg = sendgrid.SendGridAPIClient('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')
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


if __name__ == "__main__":
    send_welcome_mail('mats.deraymaeker@gmail.com', 'Bob')
