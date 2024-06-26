import os
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv
import time
import publisher_mailing

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
            loggera = ("Error Response:", response.body)
            publisher_mailing.sendLogsToMonitoring("Error adding contact", loggera, False)

    except Exception as e:
        # Handle exceptions
        print("Error:", e)
        logerr = ("Error:", e)
        publisher_mailing.sendLogsToMonitoring("Error adding contact", logerr, False)


def delete_contact_by_id(email, first_name, last_name, id, tel):
    # Replace with your SendGrid API key
        SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY_CONTACTS')

        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)

        # Replace with the actual external ID
        external_id_to_delete = id

        # Step 1: Retrieve the contact ID using the external ID
        response = sg.client.marketing.contacts.get()

        if response.status_code == 200:
            contacts = response.to_dict.get('result', [])
            contact_id = None
            for contact in contacts:
                if contact['external_id'] == external_id_to_delete:
                    contact_id = contact['id']
                    break
            if contact_id:
                # Delete the contact using the contact ID
                delete_response = sg.client.marketing.contacts.delete(query_params={'ids': contact_id})
                if delete_response.status_code == 202:
                    job_id = delete_response.to_dict['job_id']
                    print(f"Deletion job submitted successfully. Job ID: {job_id}")

                    # Check the status of the job
                    while True:
                        status_response = sg.client.marketing.jobs._(job_id).get()
                        if status_response.status_code == 200:
                            status = status_response.to_dict['status']
                            print(f"Job status: {status}")
                            if status == 'completed':
                                print("Contact deletion completed successfully.")
                                break
                            elif status == 'failed':
                                print("Contact deletion failed.")
                                break
                            else:
                                # Wait before checking again
                                time.sleep(5)
                        else:
                            loga = ("Error checking job status:", status_response.status_code, status_response.body)
                            publisher_mailing.sendLogsToMonitoring("Error checking job status", loga, False)
                            break
                else:
                    logb = ("Error deleting contact:", delete_response.status_code, delete_response.body)
                    publisher_mailing.sendLogsToMonitoring("Error deleting contact", logb, False)
            else:
                logc = ("Contact not found.")
                publisher_mailing.sendLogsToMonitoring("Contact not found.", logc, False)
        else:
            lodd = ("Error retrieving contacts:", response.status_code, response.body)
            publisher_mailing.sendLogsToMonitoring("Error retrieving contacts", lodd, False)