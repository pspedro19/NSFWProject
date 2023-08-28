# Import necessary libraries
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import os
from google_drive_downloader import GoogleDriveDownloader as gdd
from clip_interrogator import Config, Interrogator
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Initialize the FastAPI app
app = FastAPI()

# Initialize the Clip Interrogator configuration and Interrogator
config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

# Define a function to process images and generate prompts
def image_to_prompt(image, mode):
    prompt = ci.get_prompt_from_image(image, mode=mode)
    return prompt

# Define a function to process videos and generate prompts
def video_to_prompt(video_path, mode):
    # Process video and get its analysis results
    with open(video_path, "rb") as video_file:
        video_data = video_file.read()
    video_stream = BytesIO(video_data)
    video_image = Image.open(video_stream)
    prompt = image_to_prompt(video_image, mode=mode)  # Modify the mode as needed
    return prompt

# Initialize Google Drive API
api_service_name = "drive"
api_version = "v3"
creds = None  # Use your credentials here
service = build(api_service_name, api_version, credentials=creds)

# Define a route to process videos
@app.post("/api/process_videos/")
async def process_videos(folder_info: dict):
    try:
        # Extract the folder URL from the request
        folder_url = folder_info.get("folder_url")
        if not folder_url:
            raise HTTPException(status_code=400, detail="Folder URL is missing in the request")

        # Extract the folder ID from the URL
        folder_id = folder_url.split("/")[5].split("?")[0]

        # List video filenames in the Google Drive folder using Google Drive API
        query = f"'{folder_id}' in parents and mimeType='video/mp4'"
        response = service.files().list(q=query, fields="files(name)").execute()
        video_filenames = [file.get("name") for file in response.get("files", [])]

        # Process the videos and return results
        results = []
        for video_filename in video_filenames:
            try:
                # Download video data from Google Drive
                video_path = os.path.join('videos', video_filename)
                download_url = f"https://drive.google.com/uc?id={video_filename}"
                os.system(f"wget {download_url} -O {video_path}")
    
                # Process video and get its analysis results
                prompt = video_to_prompt(video_path, mode="best")  # Modify the mode as needed
                analysis_result = {"video": video_filename, "prompt": prompt}
                results.append(analysis_result)
            except Exception as e:
                results.append({"video": video_filename, "error": str(e)})

        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Run the app using Gunicorn on port 4000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
