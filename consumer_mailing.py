import pika
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
                    <xs:element name="Timestamp" type="xs:dateTime" />
                    <xs:element name="Status" type="xs:string" />
                    <xs:element name="SystemName" type="xs:string" />
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
                <xs:element name="routing_key" type="xs:string"/>
                <xs:element name="user_id" type="xs:string"/>
                <xs:element name="first_name" type="xs:string"/>
                <xs:element name="last_name" type="xs:string"/>
                <xs:element name="email" type="xs:string"/>
                <xs:element name="telephone" type="xs:string"/>
                <xs:element name="birthday" type="xs:date"/>
                <xs:element name="address">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="country" type="xs:string"/>
                            <xs:element name="state" type="xs:string"/>
                            <xs:element name="city" type="xs:string"/>
                            <xs:element name="zip" type="xs:string"/>
                            <xs:element name="street" type="xs:string"/>
                            <xs:element name="house_number" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="company_email" type="xs:string" minOccurs="0"/>
                <xs:element name="company_id" type="xs:string" minOccurs="0"/>
                <xs:element name="source" type="xs:string" minOccurs="0"/>
                <xs:element name="user_role">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:enumeration value="Speaker"/>
                            <xs:enumeration value="Individual"/>
                            <xs:enumeration value="Employee"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="invoice">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:enumeration value="Yes"/>
                        </xs:restriction>
                    </xs:simpleType>
                </xs:element>
                <xs:element name="calendar_link" />
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
            else:
                print(f"No handler defined for XML type: {xml_type}")
        else:
            print(f"Received invalid XML: {root_element}")
    
    except Exception as e:
        print(f"Error processing message: {str(e)}")

# Connect to RabbitMQ server
credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='10.2.160.51', credentials=credentials))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='mailing', durable=True)

# Set up consumer to receive messages from the queue
channel.basic_consume(queue='mailing', on_message_callback=callback, auto_ack=True)

# Start consuming messages
print('Waiting for messages...')
channel.start_consuming()