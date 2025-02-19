import json
from pika import BlockingConnection, ConnectionParameters
from pymongo import MongoClient
from app.book.service_layer.book_mongo_handler import MongoDBHandler
from app.infrastructure.mongodb.mongodb import books_collection


def consume_book_updates():
    connection = BlockingConnection(ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="book_updates")

    def callback(ch, method, properties, body):
        event = json.loads(body)
        if event["event_type"] == "book_created":
            books_collection.insert_one(event["book_data"])
        elif event["event_type"] == "book_updated":
            books_collection.update_one(
                {"_id": event["book_id"]},
                {"$set": event["book_data"]},
            )
        elif event["event_type"] == "book_deleted":
            books_collection.delete_one({"_id": event["book_id"]})

    channel.basic_consume(queue="book_updates", on_message_callback=callback, auto_ack=True)
    print("Waiting for messages. To exit, press CTRL+C")
    channel.start_consuming()


# Run the consumer in a separate thread or process
import threading

consumer_thread = threading.Thread(target=consume_book_updates)
consumer_thread.start()
