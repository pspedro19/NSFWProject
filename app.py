# Import necessary libraries
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import os
import subprocess
from google_drive_downloader import GoogleDriveDownloader as gdd
from clip_interrogator import Config, Interrogator

# Initialize the FastAPI app
app = FastAPI()

# Define a function to set up the required dependencies
def setup():
    install_cmds = [
        ['pip', 'install', 'gradio'],
        ['pip', 'install', 'open_clip_torch'],
        ['pip', 'install', 'clip-interrogator'],
    ]
    for cmd in install_cmds:
        print(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8'))

# Call the setup function to install the required dependencies
setup()

# Initialize the Clip Interrogator configuration
config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

# Define a function to process images and generate prompts
def image_to_prompt(image, mode):
    # Rest of the function remains the same

# Define a route to process videos
@app.post("/api/process_videos/")
async def process_videos():
    try:
        # Replace with the Google Drive folder URL
        folder_url = "https://drive.google.com/drive/folders/1N6KpWfYhOt_s2I6jGEIKiERLMY2J8Sqa?usp=sharing"

        # Extract the folder ID from the URL
        folder_id = folder_url.split("/")[5].split("?")[0]

        # List video filenames in the local "videos" directory
        videos_folder = 'videos'
        video_filenames = os.listdir(videos_folder)

        # Process the videos and return results
        results = []
        for video_filename in video_filenames:
            # Process video and get its analysis results
            video_path = os.path.join(videos_folder, video_filename)
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
            video_stream = BytesIO(video_data)
            video_image = Image.open(video_stream)
            prompt = image_to_prompt(video_image, mode="best")  # Modify the mode as needed
            analysis_result = {"video": video_filename, "prompt": prompt}
            results.append(analysis_result)

        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Run the app using Gunicorn on port 4000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
