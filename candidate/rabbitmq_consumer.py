import pika
import json


def receive_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        'localhost'
    ))
    channel = connection.channel()
    channel.queue_declare(queue='data')
    message = None
    method_frame, header_frame, body = channel.basic_get(queue='data')
    if method_frame:
        # print(body)
        message = json.loads(body.decode())
        # channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        # not acknowledge the data, so it won't delete from the queue
    else:
        message = None
        print("No message received")
    connection.close()
    return message

