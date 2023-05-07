import urllib.request
import os
import requests
from typing import Any, Optional, Dict
import pika
import json


def download_file(url: str, folder: str) -> None:
    """
    Downloads a file from a URL and saves it to a specified folder.

    Parameters:
    url (str): The URL of the file to download.
    folder (str): The name of the folder to save the file in.

    Returns:
    None
    """
    file_name = url.split("/")[-1]
    file_path = os.path.join(os.getcwd(), folder)

    # Create the folder if it doesn't exist
    os.makedirs(file_path, exist_ok=True)
    file_path = os.path.join(file_path, file_name)
    urllib.request.urlretrieve(url, file_path)
    print("File downloaded and saved to", file_path)


def upload_file(url: str, file_path: str) -> Any:
    """
    Uploads a file to the specified API endpoint URL using the `requests` library.

    Args:
        url (str): The URL of the API endpoint.
        file_path (str): The local path to the file that you want to upload.

    Returns:
        The response object returned by the `requests.post` method.
    """
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    return response


def upload_file_binary(
    url: str, file_name: str, binary_file: bytes, file_format: str
) -> str:
    """
    Sends a file as multipart/form data to an API endpoint.

    Args:
        url (str): The URL of the API endpoint.
        file_name (str): File name of the binary file.
        binary_file (bytes): The path to the file to be uploaded.
        file_format (str): File format of the binary file

    Returns:
        str: The response from the API as a string.
    """
    files = {"file": (file_name, binary_file, file_format)}
    response = requests.post(url, files=files)
    return (response.text, response.status_code)


def put_message_in_queue(json_config: str, queue_name: str, message: str) -> None:
    """
    Put a message into a RabbitMQ queue.

    Args:
        json_config (str): Config credential file.
        queue_name (str): The name of the queue to put the message into.
        message (str): The message to put into the queue.

    Returns:
        None
    """
    json_config = os.path.join(os.getcwd(), json_config)

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

    # Declare a queue
    channel.queue_declare(queue=queue_name)

    message = json.dumps(message)
    # Publish the message to the queue
    channel.basic_publish(exchange="", routing_key=queue_name, body=message)

    # Close the connection to RabbitMQ server
    connection.close()


def consume_single_message(json_config: str, queue_name: str) -> Optional[Dict]:
    """
    Consumes a single message from the specified RabbitMQ queue and returns it as a dictionary.

    Args:
        json_config (str): Config credential file.
        queue_name (str): The name of the queue to consume from.

    Returns:
        dict or None: If a message was consumed from the queue, returns the message as a dictionary.
                      Otherwise, returns None.
    """
    json_config = os.path.join(os.getcwd(), json_config)

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
    channel.queue_declare(queue=queue_name)

    method_frame, header_frame, body = channel.basic_get(
        queue=queue_name, auto_ack=True
    )
    if method_frame:
        message_dict = json.loads(body.decode("utf-8"))
        connection.close()
        return message_dict
    else:
        connection.close()
        return None


def flush_queue(json_config: str, queue_name: str) -> None:
    """
    Flushes all messages from a RabbitMQ queue. DO NOT USE THIS IN PRODUCTION!

    Args:
        json_config (str): Config credential file.
        queue_name (str): The name of the queue to flush.

    Returns:
        None
    """
    json_config = os.path.join(os.getcwd(), json_config)

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

    # Declare the queue in case it doesn't exist
    channel.queue_declare(queue=queue_name)

    # Check if the queue is empty
    queue_info = channel.queue_declare(queue=queue_name, passive=True)
    message_count = queue_info.method.message_count
    if message_count == 0:
        # If the queue is empty, close the connection and return
        channel.close()
        connection.close()
        return

    else:
        for x in range(message_count):
            method_frame, header_frame, body = channel.basic_get(
                queue=queue_name, auto_ack=True
            )

    # Close the connection and channel
    channel.close()
    connection.close()
