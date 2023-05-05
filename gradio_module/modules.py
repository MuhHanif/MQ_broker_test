import urllib.request
import os
import requests
from typing import Any


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

    Raises:
        requests.exceptions.RequestException: If the request fails for any reason.

    Example Usage:
        >>> upload_file('http://localhost:5959/file', 'path/to/your/file.txt')
        <Response [200]>
    """
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    return response
