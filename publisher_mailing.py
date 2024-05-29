import datetime
import pika
import os
import xml.etree.ElementTree as ET  # Importing ElementTree to handle XML
import logging
import sys

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the level of this logger.
# DEBUG, INFO, WARNING, ERROR, CRITICAL can be used depending on the granularity of log you want.
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
s_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
s_handler.setLevel(logging.DEBUG)  # Set level to DEBUG

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
s_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
s_handler.setFormatter(s_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(s_handler)


def sendLogsToMonitoring(functionName, logMessage, isError):
    # Construct XML document for LogEntry
    log_elem = ET.Element('LogEntry')

    # Define elements with provided values
    elements = [
        ('SystemName', 'Mailing'),
        ('FunctionName', str(functionName)),
        ('Logs', str(logMessage)),
        ('Error', 'true' if isError else 'false'),
        ('Timestamp', datetime.now().isoformat()),  # Timestamp in ISO 8601 format
    ]

    for elem_name, elem_value in elements:
        ET.SubElement(log_elem, elem_name).text = elem_value

    # Create XML string
    xml_str = ET.tostring(log_elem, encoding='utf-8', method='xml')
    xml_str = xml_str.decode('utf-8')  # Convert bytes to string

    # Publish Log XML object to RabbitMQ
    publish_xml_message('amq.topic', 'logs', xml_str)


def publish_xml_message(exchange_name, routing_key, xml_str):
    # Publish the XML object to RabbitMQ
    credentials = pika.PlainCredentials(os.getenv('RABBITMQ_USER'), os.getenv('RABBITMQ_PASSWORD'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'), credentials=credentials))
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

    # Publish the message
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=xml_str)

    # Close the connection
    connection.close()
        
    logger.info(f"XML message published to RabbitMQ with routing key '{routing_key}'")