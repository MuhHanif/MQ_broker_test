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
with open(json_config, "r") as conf:
    config = json.load(conf)


# function that executed in the web ui
def read_binary_file(file) -> str:
    # =============[send both image and message to dummy server]============= #
    with open(json_config, "r") as conf:
        config = json.load(conf)

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
        output = response.text
    else:
        output = "upload failed"

    return output  # + str(binary_data)


def retrieve_message():
    output_result = consume_single_message(
        json_config="conf.json", queue_name=config["queue_response"]
    )

    response = requests.get(output_result["file_uri"]["conversation"])

    return response.text


demo = gr.Blocks()
with demo:
    gr.Markdown("# whisper queue demo")

    with gr.Tabs():
        # upload audio files to queue
        with gr.TabItem("upload audio"):
            with gr.Row():
                # file input
                input_file = gr.File()
            with gr.Row():
                # prompted output if failed or succeed
                text_output2 = gr.Textbox()

            # execute function
            upload = gr.Button("send to queue")

        # download vtt files from queue
        with gr.TabItem("download vtt"):
            with gr.Row():
                image_output = gr.TextArea()
            retrieve = gr.Button("retrieve queue")

    upload.click(read_binary_file, inputs=input_file, outputs=[text_output2])
    retrieve.click(retrieve_message, inputs=None, outputs=image_output)

demo.launch(server_name="0.0.0.0", server_port=9789)
