import pika
import os
from lxml import etree
from io import BytesIO
import MailDynamic
from dotenv import load_dotenv
import Mailcontacts
import requests
import json
import publisher_mailing
load_dotenv()

# XSD schema definition
xsd_string = {
    'Heartbeat': '''
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:element name="Heartbeat">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Timestamp" type="xs:dateTime"/>
                <xs:element name="Status" type="xs:string"/>
                <xs:element name="SystemName" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    
</xs:schema>
    ''',
    'user': '''
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:element name="user">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="routing_key">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:minLength value="1"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="crud_operation">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:enumeration value="create"/>
                            <xs:enumeration value="update"/>
                            <xs:enumeration value="delete"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="id">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:minLength value="1"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="first_name" type="xs:string" nillable="true"/>
                <xs:element name="last_name" type="xs:string" nillable="true"/>
                <xs:element name="email" type="xs:string" nillable="true"/>
                <xs:element name="telephone" type="xs:string" nillable="true"/>
                <xs:element name="birthday">
                    <xs:simpleType>
                        <xs:union>
                            <xs:simpleType>
                                <xs:restriction base='xs:string'>
                                    <xs:length value="0"/>
                                </xs:restriction>
                            </xs:simpleType>
                            <xs:simpleType>
                                <xs:restriction base='xs:date' />
                            </xs:simpleType>
                        </xs:union>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="address">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="country" type="xs:string" nillable="true"/>
                            <xs:element name="state" type="xs:string" nillable="true"/>
                            <xs:element name="city" type="xs:string" nillable="true"/>
                            <xs:element name="zip">
                                <xs:simpleType>
                                    <xs:union>
                                        <xs:simpleType>
                                            <xs:restriction base='xs:string'>
                                                <xs:length value="0"/>
                                            </xs:restriction>
                                        </xs:simpleType>
                                        <xs:simpleType>
                                            <xs:restriction base='xs:integer' />
                                        </xs:simpleType>
                                    </xs:union>
                                </xs:simpleType>
                            </xs:element>
                            <xs:element name="street" type="xs:string" nillable="true"/>
                            <xs:element name="house_number">
                                <xs:simpleType>
                                    <xs:union>
                                        <xs:simpleType>
                                            <xs:restriction base='xs:string'>
                                                <xs:length value="0"/>
                                            </xs:restriction>
                                        </xs:simpleType>
                                        <xs:simpleType>
                                            <xs:restriction base='xs:integer' />
                                        </xs:simpleType>
                                    </xs:union>
                                </xs:simpleType>
                            </xs:element>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="company_email" type="xs:string" nillable="true"/>
                <xs:element name="company_id" type="xs:string" nillable="true"/>
                <xs:element name="source" type="xs:string"  nillable="true"/>
                <xs:element name="user_role">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:enumeration value="speaker"/>
                            <xs:enumeration value="individual"/>
                            <xs:enumeration value="employee"/>
                            <xs:enumeration value=""/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="invoice" type="xs:string" nillable="true"/>
                <xs:element name="calendar_link" type="xs:string" nillable="true"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>

</xs:schema>

''',
'invoice':'''
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

    <xs:element name="invoice">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="routing_key">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:minLength value="1"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="filename">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:minLength value="1"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="email">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="pdfBase64">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:minLength value="1"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>

</xs:schema>
''',

}

# Function to validate XML against embedded XSD schema
def validate_xml(xml_str):
    try:
        root = etree.fromstring(xml_str)
        if root.tag in xsd_string:
            xsd_str = xsd_string[root.tag]
            xmlschema = etree.XMLSchema(etree.fromstring(xsd_str))
            xmlparser = etree.XMLParser(schema=xmlschema)
            etree.fromstring(xml_str, xmlparser)
            return True, root  # Valid XML and root element
        else:
            logvalidatexml = (f"No schema available for the received XML root element '{root.tag}'")
            publisher_mailing.sendLogsToMonitoring("Invalid xml", logvalidatexml, False)
            return False, f"No schema available for the received XML root element '{root.tag}'"
    except etree.XMLSchemaError as e:
        return False, str(e)  # Invalid XML

def send_welcome_mail(root_element):
    try:
        email = root_element.find('email').text
        firstname = root_element.find('first_name').text
        lastname = root_element.find('last_name').text
        id = root_element.find('id').text
        tel = root_element.find('telephone').text
        
        add_service_id(id,'mailing',id)
        MailDynamic.send_welcome_mail(email, firstname)
        Mailcontacts.add_user_to_contacts(email,firstname,lastname, id, tel)
        
    except Exception as e:
        log = (f"Error sending welcome mail: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error sending welcome mail", log, False)


def update_contact(root_element):
    try:
        email = root_element.find('email').text
        firstname = root_element.find('first_name').text
        lastname = root_element.find('last_name').text
        id = root_element.find('id').text
        tel = root_element.find('telephone').text
        
        Mailcontacts.add_user_to_contacts(email,firstname,lastname, id, tel)
        
    except Exception as e:
        log = (f"Error updating contact: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error updating contact", log, False)


def delete_contact(root_element):
    try:
        email = root_element.find('email').text
        firstname = root_element.find('first_name').text
        lastname = root_element.find('last_name').text
        id = root_element.find('id').text
        tel = root_element.find('telephone').text
        
        Mailcontacts.delete_contact_by_id(email,firstname,lastname, id, tel)
        
    except Exception as e:
        log = (f"Error delete contact: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error delete contact", log, False)

def send_invoice(root_element):
    try:
        filename = root_element.find('filename').text
        email = root_element.find('email').text
        invoice = root_element.find('pdfBase64').text
        
        MailDynamic.send_invoice_mail(email,filename,invoice)
        
    except Exception as e:
        log = (f"Error sending invoice mail: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error sending invoice mail", log, False)

def handle_service_down(root_element,status):
    try:
        timestamp = root_element.find('Timestamp').text
        name = root_element.find('SystemName').text

        print(name,timestamp, status)
        MailDynamic.send_mail_service_down(name, status, timestamp)

    except Exception as e:
        log = (f"Error sending service down mail: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error sending service down mail", log, False)

def handle_service_up(root_element,status):
    try:
        timestamp = root_element.find('Timestamp').text
        name = root_element.find('SystemName').text

        print(name,timestamp, status)
        MailDynamic.send_mail_service_up(name, status, timestamp)

    except Exception as e:
        log = (f"Error sending service up mail: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error sending service up mail", log, False)

def add_service_id(master_uuid, service, service_id):
    url = f"http://{os.getenv('RABBITMQ_HOST')}:6000/addServiceId"
    payload = {
        "MasterUuid": master_uuid,
        "Service": service,
        "ServiceId": service_id
    }

    headers = {
        "Content-Type": "application/json"  # Set content type to JSON
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            log = (f"Unexpected response: {response.status_code} - {response.text}")
            publisher_mailing.sendLogsToMonitoring("Unexpected response", log, False)
            return None
            
    except requests.exceptions.RequestException as e:
        logg = (f"Error during request: {e}")
        publisher_mailing.sendLogsToMonitoring("Error during request", logg, False)
        return None


# Callback function for consuming messages
def callback(ch, method, properties, body):
    try:
        xml_content = body.decode('utf-8')
        is_valid, root_element = validate_xml(xml_content)
        
        if is_valid:
            xml_type = root_element.tag
            print(f"Received valid '{xml_type}' XML:")
            print(xml_content)
            
            if xml_type == 'user':
                crud = root_element.find('crud_operation').text
                routingkey = root_element.find('routing_key').text
                if crud == 'create':
                    send_welcome_mail(root_element)
                elif crud == 'update':
                    update_contact(root_element)
                elif crud == 'delete':
                    if routingkey == 'user.facturatie':
                        delete_contact(root_element)
                    log = (f"Only soft delete from: {routingkey}")
                    publisher_mailing.sendLogsToMonitoring("Only soft delete", log, False)
                else:
                    loga = (f"No such crud operation: {crud}")
                    publisher_mailing.sendLogsToMonitoring("No such crud operation", loga, False)
            elif xml_type == 'Heartbeat':
                status = root_element.find('Status').text
                if status.lower() == 'inactive':
                    handle_service_down(root_element, status)
                elif status.lower() == 'active':
                    handle_service_up(root_element, status)
            elif xml_type == 'invoice':
                send_invoice(root_element)
            else:
                logb = (f"No handler defined for XML type: {xml_type}")
                publisher_mailing.sendLogsToMonitoring("No handler defined for XML type", logb, False)
        else:
            logc = (f"Received invalid XML: {root_element}")
            publisher_mailing.sendLogsToMonitoring("Received invalid XML", logc, False)

    
    except Exception as e:
        logd = (f"Error processing message: {str(e)}")
        publisher_mailing.sendLogsToMonitoring("Error processing message", logd, False)

# Connect to RabbitMQ server
credentials = pika.PlainCredentials(os.getenv('RABBITMQ_USER'), os.getenv('RABBITMQ_PASSWORD'))
connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'), credentials=credentials))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='mailing', durable=True)

# Set up consumer to receive messages from the queue
channel.basic_consume(queue='mailing', on_message_callback=callback, auto_ack=True)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()