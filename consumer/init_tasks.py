import json
import os
from threading import Thread
import pika
from pymongo import MongoClient
from structlog import get_logger

logger = get_logger()

database_url = os.getenv("ACCOUNTS_DATABASE_URL")


def get_database_collection(collection_name: str):
    client = MongoClient(database_url)
    db = client["pia"]
    return db[collection_name]


def consume_messages():
    connection_established = False
    while connection_established is False:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq-service",  # Service name
                    port=5672,  # Default AMQP port
                    virtual_host="/",
                    credentials=pika.PlainCredentials("guest", "guest"),
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue="task_queue", durable=True)
            connection_established = True
        except:
            connection_established = False

    def callback(ch, method, properties, body):
        logger.info(event="Received message", message=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        decoded_data = json.loads(body.decode("utf-8"))

        created_account = get_database_collection("accounts").insert_one(
            {"user_id": str(decoded_data["user_id"])}
        )

        logger.info(
            event="Created account for user",
            account_id=str(created_account.inserted_id),
            user_id=str(decoded_data["user_id"]),
        )

    channel.basic_consume(
        queue="task_queue", on_message_callback=callback, auto_ack=False
    )
    logger.info(event="Waiting for messages.")
    channel.start_consuming()


def start_consumer():
    consumer_thread = Thread(target=consume_messages)
    consumer_thread.start()


if __name__ == "__main__":
    start_consumer()
