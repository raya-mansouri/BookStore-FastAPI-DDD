import aio_pika
import json


async def publish_event(event_data):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    await channel.queue_declare(queue="reservation_events", durable=True)

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(event_data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Make message persistent
        ),
        routing_key="reservation_events",  # The queue to publish to
    )

    connection.close()
