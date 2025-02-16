import pika
import json


def publish_event(event_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="reservation_events", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="reservation_events",
        body=json.dumps(event_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ),
    )

    connection.close()
