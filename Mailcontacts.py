import os
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv

def add_user_to_contacts(email, first_name, last_name):
    try:
        # Load environment variables from .env file
        load_dotenv(encoding="latin-1")

        # Create SendGrid API client
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY_CONTACTS'))

        # Prepare data to add contact
        data = {
            "contacts": [
                {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
            ]
        }

        # Call the SendGrid API to add contact
        response = sg.client.marketing.contacts.put(
            request_body=data
        )

        # Print response details
        print("Status Code:", response.status_code)
        print("Response Body:", response.body)
        print("Headers:", response.headers)

        # Check for errors in response body
        if response.status_code != 202:
            print("Error Response:", response.body)

    except Exception as e:
        # Handle exceptions
        print("Error:", e)

# Example usage:
add_user_to_contacts("manu.overath@student.ehb.be", "Axel", "Overath")
