from flask import Flask

import init_tasks

app = Flask(__name__)


init_tasks.start_consumer()


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5002)
