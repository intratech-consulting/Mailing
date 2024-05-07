#!/usr/bin/env python3
import os
import ssl
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

context = ssl.create_default_context()


# from address we pass to our Mail object, edit with your name
FROM_EMAIL = 'mats.deraymaeker@student.ehb.be'

# update to your dynamic template id from the UI
TEMPLATE_ID = 'd-b3b117e3099a4b30baf380342afbd54f'

# list of emails and preheader names, update with yours
TO_EMAILS = [('mats.deraymaeker@gmail.com', 'James Holden')]
             # update email and name
             #('your_email+1@domain.com', 'Joe Miller')]


def SendDynamic():
    """ Send a dynamic email to a list of email addresses

    :returns API response code
    :raises Exception e: raises an exception """
    # create Mail object and populate
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAILS)
    # pass custom values for our HTML placeholders
    message.dynamic_template_data = {
        'name': 'Tast Tester'
    }
    message.template_id = TEMPLATE_ID
    # create our sendgrid client object, pass it our key, then send and return our response objects
    # try:
    #     sg = SendGridAPIClient("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")
    #     response = sg.send(message)
    #     code, body, headers = response.status_code, response.body, response.headers
    #     print(f"Response code: {code}")
    #     print(f"Response headers: {headers}")
    #     print(f"Response body: {body}")
    #     print("Dynamic Messages Sent!")
    # except Exception as e:
    #     print("Error: {0}".format(e))
    # return str(response.status_code)

    try:
        sg = SendGridAPIClient("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", ssl_context=context)
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Response code: {code}")
        print(f"Response headers: {headers}")
        print(f"Response body: {body}")
        print("Dynamic Messages Sent!")
    except Exception as e:
        print("Error: {0}".format(e))


if __name__ == "__main__":
    SendDynamic()
