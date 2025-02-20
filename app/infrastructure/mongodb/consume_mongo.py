import asyncio
import json
import aio_pika
from pymongo import MongoClient
from app.book.service_layer.book_mongo_handler import MongoDBHandler
from app.infrastructure.mongodb.mongodb import books_collection


book_handler = MongoDBHandler(books_collection)


async def consume_book_updates():
    async def callback(message: aio_pika.IncomingMessage):
        async with message.process():
            event_data = json.loads(message.body)
            event_type = event_data.get("event_type")

            if event_type == "book_created":
                book_data = event_data.get("book_data")
                # Ensure that book_data is a dictionary and contains the necessary fields
                if "_id" not in book_data:
                    book_data["_id"] = event_data.get("book_id")  # Set book_id as _id if it's not in book_data
                book_handler.handle_book_created(book_data)  # Insert the book document into MongoDB

            elif event_type == "book_updated":
                book_id = event_data.get("book_id")
                book_data = event_data.get("book_data")
                book_handler.handle_book_updated(
                    {"_id": book_id},
                    {"$set": book_data},
                )
            
            elif event_type == "book_deleted":
                book_id = event_data.get("book_id")
                book_handler.handle_book_deleted({"_id": book_id})

    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    # Use passive to check for existing queue with the same properties (durable=True)
    try:
        queue = await channel.declare_queue("book_updates", durable=True, passive=True)
    except aio_pika.exceptions.AMQPChannelError:
        # If the queue does not exist or is different, declare it with the correct properties
        queue = await channel.declare_queue("book_updates", durable=True)

    await queue.consume(callback)
    print("Waiting for book_updates events. To exit press CTRL+C")
    await asyncio.Future()


# Run the consumer in a separate thread or process
# import threading

# consumer_thread = threading.Thread(target=consume_book_updates)
# consumer_thread.start()
