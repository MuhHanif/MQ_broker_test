from gradio_module.modules import *
import gradio as gr
import requests
import subprocess

# return_dict = consume_single_message(json_config="conf.json", queue_name="testing2")
# print(return_dict)

# import requests

# =====request to server

# api url
url = "http://0.0.0.0:8000"
    
# simple dummy bucket url
bucket_url = "https://dummy-bucket.treehaus.dev/audio/"

# config path
json_config = "conf.json"
with open(json_config, "r") as conf:
    config = json.load(conf)

global_uuid = [None]

# function that executed in the web ui
def read_binary_file(file, test_convert: bool = False) -> str:
    try:
        # =============[send both image and message to dummy server]============= #
        with open(json_config, "r") as conf:
            config = json.load(conf)

        upload_folder = os.path.join(os.getcwd(), "upload")  # TODO: hoist this!

        # Create the folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)

        file_name = file.name.replace(" ", "_")
        os.rename(file.name, file_name)
        print(file_name)

        print_out = "MP3 detected, skipping conversion"
        if file_name.split(".")[-1] != "mp3":
            # converted audio file path
            saved_file = os.path.join(
                upload_folder, file_name.split("/")[-1].split(".")[0] + ".mp3"
            )

            # execute ffmpeg bash script
            ffmpeg_convert = ["ffmpeg", "-i", file_name, saved_file, "-y"]
            print_out = subprocess.run(
                " ".join(ffmpeg_convert),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
        else:
            saved_file = file_name

        if not test_convert:
            response = upload_file_to_worker_queue(url=f"{url}/upload_to_queue_process/", file_path=saved_file)
            global_uuid[0] = json.loads(response.text)["queue_id"]
            return response.text
        if test_convert:
            return "converting audio to mp3 before upload sucessful"
    except Exception as e:
        return f"ERROR: {e}"

    
def queue_length():
    queue_count = requests.get(url=f"{url}/queue_length").text
    return json.loads(queue_count)["queue_length"]

def retrieve_last_transcription():
    uuid = global_uuid[0]
    if uuid != None:
        response = requests.get(url=f"{url}/transcribtion_status/{uuid}").text
        response = json.loads(response)
        if response["status"] == "transcribed":
            # conversation response
            conversation = response["output_as_text"]["conversation"]
            conversation = "\n".join(conversation)
            left_channel = response["output_as_text"]["left_channel"]
            left_channel = "\n".join(left_channel)
            right_channel = response["output_as_text"]["right_channel"]
            right_channel = "\n".join(right_channel)
            audio_transcribtion_time = round(response["output_as_text"]["audio_transcribtion_time"], 2)
            output= [conversation, left_channel, right_channel, f"{audio_transcribtion_time} second(s)"]
        else:
            output = [response["status"]]*4
    else:
        output = ["no transciption"]*4
    return output


demo = gr.Blocks()
with demo:
    gr.Markdown("# whisper queue demo")

    with gr.Tabs():
        # upload audio files to queue
        with gr.TabItem("upload audio"):

            with gr.Row():
                with gr.Column(scale=4):    
                    gr.Markdown("## upload audio")
                    # file input
                    input_file = gr.File(label="drop your audio files here")
                    # prompted output if failed or succeed
                    text_output2 = gr.Textbox(label="upload response")

                    # execute function
                    test_gradio_file_conversion = gr.Checkbox(
                        label="test audio conversion to MP3"
                    )
                    upload = gr.Button("send to queue")


                with gr.Column(scale=8):        
                    gr.Markdown("## get the last transcribed audio")
                    conversation_output = gr.TextArea(label="conversation", max_lines=5)
                    left_channel_output = gr.TextArea(label="left channel", max_lines=5)
                    right_channel_output = gr.TextArea(label="right channel",  max_lines=5)
                    time = gr.Textbox(label="transcription time")
                    retrieve = gr.Button("retrieve queue")

        # download vtt files from queue
        # with gr.TabItem("download vtt"):
            

    upload.click(
        read_binary_file,
        inputs=[input_file, test_gradio_file_conversion],
        outputs=[text_output2],
    )
    retrieve.click(retrieve_last_transcription, inputs=None, outputs=[conversation_output, left_channel_output, right_channel_output, time])

demo.launch(server_name="0.0.0.0", server_port=9789)
