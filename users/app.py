import json
import os

from bson import ObjectId
from flask import Flask, abort, request
import pika
from pymongo import MongoClient, ReturnDocument
from structlog import get_logger

logger = get_logger()

app = Flask(__name__)

users_database_url = os.getenv("USERS_DATABASE_URL")
accounts_database_url = os.getenv("ACCOUNTS_DATABASE_URL")


def get_users_db_collection(collection_name: str):
    client = MongoClient(users_database_url)
    db = client["pia"]
    return db[collection_name]


def get_accounts_db_collection(collection_name: str):
    client = MongoClient(accounts_database_url)
    db = client["pia"]
    return db[collection_name]


@app.route("/users", methods=["POST"])
def post_user():
    new_data = request.json
    try:
        insert_result = get_users_db_collection("users").insert_one(new_data)
    except Exception as e:
        logger.info(event="Failed to insert user", error=e)

    logger.info(f"Inserted data: {new_data}")

    try:
        produce_message(
            dict(event="user-created", user_id=str(insert_result.inserted_id))
        )
    except Exception as e:
        logger.warning(event="Failed to produce message", error=e)

    return {
        "status": f"Data inserted successfully with id: {insert_result.inserted_id}"
    }


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id: str):
    user = get_users_db_collection("users").find_one({"_id": ObjectId(user_id)})

    if not user:
        return abort(404, "Object not found")

    user["id"] = str(user["_id"])
    del user["_id"]
    logger.info(f"Fetched user: {user}")

    return {"user": user} if user else {"status": "Object not found"}


@app.route("/users/<user_id>/accounts/<account_id>", methods=["GET"])
def get_user_account(user_id: str, account_id: str):
    account = get_accounts_db_collection("accounts").find_one(
        {"_id": ObjectId(account_id)}
    )
    if not account:
        return abort(404, "Object not found")

    account["id"] = str(account["_id"])
    del account["_id"]
    logger.info(f"Fetched user: {account}")

    if user_id != account["user_id"]:
        return abort(401, description="You are not authorized to access this resource")

    return {"account": account} if account else {"status": "Object not found"}


@app.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id: str):
    update_data = request.json
    updated_user = get_users_db_collection("users").find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    if not updated_user:
        return {"status": "Object not found"}

    logger.info(f"Updated user: {updated_user}")
    return {"status": "Data updated successfully"}


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    get_users_db_collection("users").delete_one({"_id": ObjectId(user_id)})
    logger.info(f"Deleted user with id: {user_id}")

    return {"status": "User deleted successfully"}


# Produce a message
def produce_message(message):
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

    # Serialize the message
    serialized_message = json.dumps(message)

    # Send the message
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=serialized_message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    connection.close()
    logger.info(event=f"Produced message", message=serialized_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
