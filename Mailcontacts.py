import os
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv

def add_user_to_contacts(email, first_name, last_name, id, tel):
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
                    "last_name": last_name,
                    "phone_number_id": tel,
                    "external_id": id
                }
            ]
        }

        # Call the SendGrid API to add contact
        response = sg.client.marketing.contacts.put(
            request_body=data
        )

        # Print response details
        # print("Status Code:", response.status_code)
        # print("Response Body:", response.body)
        # print("Headers:", response.headers)

        # Check for errors in response body
        if response.status_code != 202:
            print("Error Response:", response.body)

    except Exception as e:
        # Handle exceptions
        print("Error:", e)


def delete_contact_by_id(email, first_name, last_name, id, tel):
    try:
        # Replace with your SendGrid API key
        SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY_CONTACTS')

        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)

        # Replace with the actual external ID
        external_id_to_delete = 'EXTERNAL_ID_TO_DELETE'

        # Step 1: Retrieve the contact ID using the external ID
        response = sg.client.marketing.contacts.get()

        if response.status_code == 200:
            contacts = response.to_dict.get('result', [])
            contact_id = None
            for contact in contacts:
                if contact['custom_fields']['external_id'] == external_id_to_delete:
                    contact_id = contact['id']
                    break
            if contact_id:
                # Step 2: Delete the contact using the contact ID
                delete_response = sg.client.marketing.contacts.delete(query_params={'ids': contact_id})
                if delete_response.status_code == 204:
                    print("Contact deleted successfully.")
                else:
                    print("Error deleting contact:", delete_response.status_code, delete_response.body)
            else:
                print("Contact not found.")
        else:
            print("Error retrieving contacts:", response.status_code, response.body)
    except Exception as e:
        # Handle exceptions
        print("Error:", e)