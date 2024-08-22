import pika
import json


def send_massage(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        # channel.queue_delete(queue='data')
        channel.queue_declare(queue='data')
        channel.queue_purge(queue='data')  # to delete the previous msgs from the queue
        message_json = json.dumps(message)
        channel.basic_publish(exchange='', routing_key='data', body=message_json, properties=pika.BasicProperties(
                expiration='300000'  # Message TTL in milliseconds
            ))
        connection.close()
    except Exception as e:
        print(e)
