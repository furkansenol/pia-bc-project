import os
import requests

from flask import Flask, request
from structlog import get_logger

logger = get_logger()

app = Flask(__name__)

backend_url = os.getenv("BACKEND_URL")


@app.route("/", methods=["POST"])
def handle_post():
    logger.info(event="POST endpoint called", url=backend_url)
    response = requests.post(
        f"{backend_url}/users",
        json=request.json,
    )

    return response.text


@app.route("/", methods=["PATCH"])
def handle_patch():
    logger.info(event="PATCH endpoint called")
    response = requests.patch(
        f"{backend_url}/users/{request.json.get('id')}",
        json=request.json,
    )

    return response.text


@app.route("/", methods=["GET"])
def get_user():
    logger.info(event="GET endpoint called")
    user_id = request.args.get("user_id")
    response = requests.get(f"{backend_url}/users/{user_id}")

    return response.text


@app.route("/accounts", methods=["GET"])
def get_user_account():
    logger.info(event="GET endpoint called")
    user_id = request.args.get("user_id")
    account_id = request.args.get("account_id")
    response = requests.get(f"{backend_url}/users/{user_id}/accounts/{account_id}")

    return response.text


@app.route("/", methods=["DELETE"])
def handle_delete():
    logger.info(event="DELETE endpoint called")
    response = requests.delete(
        f"{backend_url}/users/{request.json.get('id')}",
    )

    return response.text


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
