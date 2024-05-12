# # Import the SSL module
# import ssl

# # Disable SSL certificate verification
# ssl._create_default_https_context = ssl._create_unverified_context

# # Import necessary modules
# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# # Define your email message
# message = Mail(
#     from_email='mats.deraymaeker@student.ehb.be',
#     to_emails='jarne.degraeve@telenet.be',
#     subject='Het werkt!!!! HELLL YEAH',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')

# try:
#     sg = SendGridAPIClient("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")
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(e)


# # try:
# #     # Initialize SendGrid client with your API key
# #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

# #     # Send the email
# #     response = sg.send(message)

# #     # Print response details
# #     print(response.status_code)
# #     print(response.body)
# #     print(response.headers)
# except Exception as e:
#     # Print any exceptions that occur
#     print(e)

import ssl
import MailDynamic

MailDynamic.send_welcome_mail('mats.deraymaeker@gmail.com', 'Mats')
