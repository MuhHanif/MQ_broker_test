import pika
import json
import os
from typing import Callable


def consumer_queue(json_config: str) -> None:
    # read config file for credentials and queue
    with open(json_config, "r") as conf:
        config = json.load(conf)

    # Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
    url = os.environ.get(
        "CLOUDAMQP_URL",
        config["credential"],
    )
    params = pika.URLParameters(url)

    # Set up connection parameters
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare the queue to consume from
    channel.queue_declare(queue=config["queue"])

    # Define a callback function to handle incoming messages
    def callback(ch, method, properties, body, arguments):
        print("Received message:")
        print(ch, method, properties)
        print(json.loads(body))
        print(arguments)

    # Start consuming messages
    channel.basic_consume(
        queue=config["queue"],
        on_message_callback=callback,
        auto_ack=True,
        arguments=(arguments,),
    )
    print("Waiting for messages. To exit, press CTRL+C")
    channel.start_consuming()


consumer_queue("conf.json")
