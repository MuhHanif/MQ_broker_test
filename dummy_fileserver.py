# main api function using fast api
from fastapi import FastAPI, File, UploadFile, HTTPException
from queue import Queue
import os
import configparser
import json
import time
import uvicorn

app = FastAPI()


@app.get("/testing/{name}")
async def test_connection(name: str):
    return {"message": f"Hello, {name}!"}


@app.post("/upload/audio/")
async def upload_audio_file_test_upload(file: UploadFile = File(...)) -> dict:
    """
    Endpoint that accepts an audio file and saves it to a specified folder.

    Args:
        file (UploadFile): The audio file to upload.

    Returns:
        dict: A JSON object containing the filename of the uploaded file.
    """
    # Specify the folder where the file will be saved
    upload_folder = os.getcwd() + "/dummy_file_server/audio"

    # Create the folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Check if the uploaded file is an audio file
    valid_extensions = [".mp3", ".wav", ".ogg"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="File must be an audio file")

    # Save the file to the specified folder
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # im disabling using queue for now
    # contents: bytes = await file.read()
    # audio_queue.put(contents)

    return {"message": "audio uploaded"}


@app.post("/upload/vtt/")
async def upload_audio_file_test_upload(file: UploadFile = File(...)) -> dict:
    """
    Endpoint that accepts an audio file and saves it to a specified folder.

    Args:
        file (UploadFile): The audio file to upload.

    Returns:
        dict: A JSON object containing the filename of the uploaded file.
    """
    # Specify the folder where the file will be saved
    upload_folder = os.getcwd() + "/dummy_file_server/vtt"

    # Create the folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Check if the uploaded file is an audio file
    valid_extensions = [".vtt", ".srt"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="File must be a vtt file")

    # Save the file to the specified folder
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # im disabling using queue for now
    # contents: bytes = await file.read()
    # audio_queue.put(contents)

    return {"message": "text transcription uploaded"}


uvicorn.run(app, port=8000, host="0.0.0.0")
