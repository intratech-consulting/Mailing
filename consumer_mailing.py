import pika
from lxml import etree
from io import BytesIO

# XSD schema definition
xsd_string = '''
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
'''

def validate_xml(xml_string):
    # Parse XSD schema
    xsd_doc = etree.parse(BytesIO(xsd_string.encode('utf-8')))
    xsd = etree.XMLSchema(xsd_doc)

    # Parse XML input
    xml_doc = etree.parse(BytesIO(xml_string.encode('utf-8')))

    # Validate XML against XSD schema
    try:
        xsd.assertValid(xml_doc)
        return True
    except etree.DocumentInvalid as e:
        print("Validation error:", e)
        return False

def process_message(ch, method, properties, body):
    print("Received XML message:")
    print(body.decode('utf-8'))

    # Parse XML and extract Status
    root = etree.fromstring(body)
    status_element = root.find("Status")

    if status_element is not None and status_element.text == "0":
        # Validate the XML message
        if validate_xml(body.decode('utf-8')):
            # Process the valid XML
            timestamp = root.find("Timestamp").text
            status = root.find("Status").text
            system_name = root.find("SystemName").text
            
            print("Timestamp:", timestamp)
            print("Status:", status)
            print("System Name:", system_name)
        else:
            print("Invalid XML received. Discarding message.")
    else:
        print("Message does not contain 'Status' element with value '0'. Ignoring.")

# RabbitMQ connection parameters
rabbitmq_host = '10.2.160.51'
queue_name = 'mailing'

# Establish connection to RabbitMQ
credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
channel = connection.channel()

# Declare the queue to consume from
channel.queue_declare(queue=queue_name, durable=True)

# Set up message consumption
channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)

print(f"Waiting for messages with 'Status' = 'Down' from the queue '{queue_name}'...")
channel.start_consuming()
