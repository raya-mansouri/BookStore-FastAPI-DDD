import aio_pika
import json


async def publish_event(event_data):
    """
    Publishes an event to the RabbitMQ queue 'reservation_events'.

    This function connects to RabbitMQ, declares the `reservation_events` queue (if it doesn't exist),
    and publishes the event data as a message to that queue. The event data is serialized into JSON
    and sent with persistent delivery mode to ensure that the message is not lost in case of a broker failure.

    :param event_data: The data to be published as an event (usually in a dictionary format).
    """

    # Establish connection to RabbitMQ server
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    # Create a channel for communication
    channel = await connection.channel()

    # Declare the 'reservation_events' queue if it doesn't already exist
    await channel.queue_declare(queue="reservation_events", durable=True)

    # Serialize the event data to JSON and send it as a message to the queue
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(event_data).encode(),  # Convert the event data to bytes
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Ensure message is persistent
        ),
        routing_key="reservation_events",  # The queue to publish the message to
    )

    # Close the connection after publishing the message
    connection.close()
