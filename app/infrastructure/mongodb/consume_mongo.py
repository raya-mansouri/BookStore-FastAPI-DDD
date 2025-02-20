import asyncio
import json
import aio_pika
from pymongo import MongoClient
from app.book.service_layer.book_mongo_handler import MongoDBHandler
from app.infrastructure.mongodb.mongodb import books_collection

# Initialize the MongoDB handler with the books collection
book_handler = MongoDBHandler(books_collection)


async def consume_book_updates():
    """
    Consumes book-related events from the 'book_updates' RabbitMQ queue and performs the necessary operations
    based on the event type. The events include creating, updating, and deleting books in MongoDB.

    This function listens for incoming messages from the RabbitMQ queue, processes them, and calls the appropriate
    methods of `book_handler` to interact with MongoDB.

    The possible event types are:
        - "book_created": Inserts a new book into the MongoDB collection.
        - "book_updated": Updates an existing book in the MongoDB collection.
        - "book_deleted": Deletes a book from the MongoDB collection.
    """

    # Callback function to process incoming messages
    async def callback(message: aio_pika.IncomingMessage):
        async with message.process():
            # Deserialize the incoming message body into a dictionary
            event_data = json.loads(message.body)
            event_type = event_data.get("event_type")

            if event_type == "book_created":
                book_data = event_data.get("book_data")
                # Ensure that book_data contains the necessary fields
                if "_id" not in book_data:
                    book_data["_id"] = event_data.get(
                        "book_id"
                    )  # Set book_id as _id if not present
                # Insert the new book into MongoDB
                book_handler.handle_book_created(book_data)

            elif event_type == "book_updated":
                book_id = event_data.get("book_id")
                book_data = event_data.get("book_data")
                # Update the existing book in MongoDB
                book_handler.handle_book_updated({"_id": book_id}, {"$set": book_data})

            elif event_type == "book_deleted":
                book_id = event_data.get("book_id")
                # Delete the book from MongoDB
                book_handler.handle_book_deleted({"_id": book_id})

    while True:
        try:
            # Connect to RabbitMQ
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("book_updates", durable=True)

                print("Waiting for book_updates events. To exit press CTRL+C")
                await queue.consume(callback)
                await asyncio.Future()  # Keeps the consumer running

        except aio_pika.exceptions.AMQPConnectionError:
            print("RabbitMQ connection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Retry connection after 5 seconds


# To run the consumer in a separate thread or process, use threading:
# import threading
# consumer_thread = threading.Thread(target=consume_book_updates)
# consumer_thread.start()
