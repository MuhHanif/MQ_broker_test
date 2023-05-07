from gradio_module.modules import *


# return_dict = consume_single_message(json_config="conf.json", queue_name="testing2")
# print(return_dict)

# import requests

# =====request to server

# api url
url = "http://0.0.0.0:8000/upload/audio/"

# simple dummy bucket url
bucket_url = "http://0.0.0.0:6544/audio/"


import gradio as gr


# function that executed in the web ui
def read_binary_file(file) -> str:
    # debug tools for clearing queue ensuring sequential operation
    flush_queue(json_config="conf.json", queue_name="testing2")

    # read as binary data for json serialization
    with open(file.name, "rb") as f:
        binary_data = f.read()

    # get file extension and bit of reformating
    file_extension = file.name.split(".")[-1]
    if file_extension == "mp3":
        file_extension = "mpeg"
    print(file.name.split("/")[-1])
    print(f"audio/{file_extension}")
    # upload to dummy file server (replace this part with s3 bucket)
    response = upload_file_binary(
        url=url,
        file_name=file.name.split("/")[-1],
        binary_file=binary_data,
        file_format=f"audio/{file_extension}",
    )

    # dummy payload format, only changing file URI for now
    payload = {
        "company_id": "63446d348baa6c988b337b22",
        "file_name": None,
        "file_uri": bucket_url,
        "model": "small",
        "priority": "normal",
        "request_uuid": "6408351c1fee0ed8f06c0716",
        "speaker1": "<5043891175>",
        "speaker2": "<5044288903>",
    }
    payload["file_uri"] = payload["file_uri"] + file.name.split("/")[-1]
    payload = json.dumps(payload)

    # enqueue message indicating that the audio file is uploaded
    output = None
    if response[1] == 200:
        put_message_in_queue(
            json_config="conf.json", queue_name="testing2", message=payload
        )
        output = payload
    else:
        output = "upload failed"

    return output  # + str(binary_data)


# gradio ui input output
inputs = gr.inputs.File()
outputs = gr.outputs.Textbox()


# start interface and executing defined function
gr.Interface(
    fn=read_binary_file, inputs=inputs, outputs=outputs, title="Whisper testing"
).launch()
