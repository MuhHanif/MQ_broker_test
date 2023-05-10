from gradio_module.modules import *
import gradio as gr
import requests
import subprocess

# return_dict = consume_single_message(json_config="conf.json", queue_name="testing2")
# print(return_dict)

# import requests

# =====request to server

# api url
url = "https://dummy-api.treehaus.dev/upload/audio/"

# simple dummy bucket url
bucket_url = "https://dummy-bucket.treehaus.dev/audio/"

# config path
json_config = "conf.json"


# function that executed in the web ui
def read_binary_file(file) -> str:
    # =============[send both image and message to dummy server]============= #
    with open(json_config, "r") as conf:
        config = json.load(conf)

    # debug tools for clearing queue ensuring sequential operation
    flush_queue(json_config="conf.json", queue_name=config["queue"])

    # read as binary data for json serialization
    # with open(file_name, "rb") as f:
    #     binary_data = f.read()

    upload_folder = os.path.join(os.getcwd(), "upload")  # TODO: hoist this!

    # Create the folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    file_name = file.name.replace(" ", "_")
    os.rename(file.name, file_name)
    print(file_name)

    if file_name.split(".")[-1] != "mp3":
        # converted audio file path
        saved_file = os.path.join(
            upload_folder, file_name.split("/")[-1].split(".")[0] + ".mp3"
        )

        # execute ffmpeg bash script
        ffmpeg_convert = ["ffmpeg", "-i", file_name, saved_file]
        print_out = subprocess.run(
            ffmpeg_convert, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        response = upload_file(url=url, file_path=saved_file)
    else:
        saved_file = file_name
        response = upload_file(url=url, file_path=file_name)
    # # get file extension and bit of reformating
    # file_extension = file_name.split(".")[-1]
    # if file_extension == "mp3":
    #     file_extension = "mpeg"

    # # upload to dummy file server (replace this part with s3 bucket)
    # response = upload_file_binary(
    #     url=url,
    #     file_name=file_name.split("/")[-1],
    #     binary_file=binary_data,
    #     file_format=f"audio/{file_extension}",
    # )

    # dummy payload format, only changing file URI for now
    payload = {
        "company_id": "63446d348baa6c988b337b22",
        "file_name": saved_file.split("/")[-1],
        "file_uri": bucket_url,
        "model": "medium",
        "priority": "normal",
        # replace request uuid with incrementing value
        "request_uuid": "6408351c1fee0ed8f06c0716",
        "speaker1": "channel1",
        "speaker2": "channel2",
    }
    payload["file_uri"] = payload["file_uri"] + saved_file.split("/")[-1]
    # payload = json.dumps(payload)
    # enqueue message indicating that the audio file is uploaded
    output = None
    if response.status_code == 200:
        put_message_in_queue(
            json_config="conf.json", queue_name=config["queue"], message=payload
        )
        output = payload
    else:
        output = "upload failed"

    # =============[wait for a response from messaging server]============= #

    output_result = consume_single_message(
        json_config="conf.json", queue_name=config["queue_response"]
    )
    flush_queue(json_config="conf.json", queue_name=config["queue_response"])

    response = requests.get(output_result["file_uri"]["conversation"])

    return response.text  # + str(binary_data)


# gradio ui input output
inputs = gr.inputs.File()
outputs = gr.outputs.Textbox()


# start interface and executing defined function
gr.Interface(
    fn=read_binary_file,
    inputs=inputs,
    outputs=outputs,
    title="Whisper Testing Sequential",
    allow_flagging="never",
).launch(server_name="0.0.0.0", server_port=9789)
