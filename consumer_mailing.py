import pika
import os
from lxml import etree
from io import BytesIO
import MailDynamic
from dotenv import load_dotenv

load_dotenv()

# XSD schema definition
xsd_string = {
    'status': '''
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

        <xs:element name="Heartbeat">
            <xs:complexType>
                <xs:sequence>
                    xs:element name="Timestamp" type="xs:dateTime"/>
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
    </xs:schema>''',

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
            return False, f"No schema available for the received XML root element '{root.tag}'"
    except etree.XMLSchemaError as e:
        return False, str(e)  # Invalid XML

def send_welcome_mail(root_element):
    try:
        email = root_element.find('email').text
        name = root_element.find('first_name').text

        MailDynamic.send_welcome_mail(email, name)

    except Exception as e:
        print(f"Error sending welcome mail: {str(e)}")

def handle_service_down(root_element,status):
    try:
        timestamp = root_element.find('Timestamp').text
        name = root_element.find('SystemName').text

        print(name,timestamp, status)
      #  MailDynamic.send_service_down(name, status, timestamp)

    except Exception as e:
        print(f"Error sending service down mail: {str(e)}")

def handle_service_up(root_element,status):
    try:
        timestamp = root_element.find('Timestamp').text
        name = root_element.find('SystemName').text

        print(name,timestamp, status)
      #  MailDynamic.send_service_up(name, status, timestamp)

    except Exception as e:
        print(f"Error sending service up mail: {str(e)}")


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
                send_welcome_mail(root_element)
            elif xml_type == 'status':
                send_welcome_mail(root_element)
                status = root_element.find('Status').text
                if status.lower() == 'down':
                    handle_service_down(root_element, status)
                elif status.lower() == 'active':
                    handle_service_up(root_element, status)
            else:
                print(f"No handler defined for XML type: {xml_type}")
        else:
            print(f"Received invalid XML: {root_element}")
    
    except Exception as e:
        print(f"Error processing message: {str(e)}")

# Connect to RabbitMQ server
credentials = pika.PlainCredentials(os.getenv('RABBITMQ_USERS'), os.getenv('RABBITMQ_USERS'))
connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'), credentials=credentials))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='mailing', durable=True)

# Set up consumer to receive messages from the queue
channel.basic_consume(queue='mailing', on_message_callback=callback, auto_ack=True)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()