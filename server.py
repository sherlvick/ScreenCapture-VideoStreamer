import socketio
import ffmpeg
import os
import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

sio = socketio.AsyncServer(cors_allowed_origins='*',async_mode='asgi')
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

app.mount("/", StaticFiles(directory="build"), name="index")
app.mount("/static", StaticFiles(directory="build/static"), name="static")
# @app.get("/fe")
# async def read_index():
#     with open("build/index.html") as f:
#         return f.read()

# Directory where you want to store the files
output_dir = "recordings"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sio_app = socketio.ASGIApp(sio,other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

@sio.on('screen_data')
async def handle_screen_data(sid, data):
    # Create a file for each client if it doesn't exist
    client_file_path = os.path.join(output_dir, f"{sid}.webm")
    with open(client_file_path, "ab") as f:
        f.write(data)
    await extract_frames(sid, client_file_path)


async def extract_frames(sid, video_file):
    # Open the video file
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_file}")
        return

    # Create a directory to store frames
    frames_dir = os.path.join(output_dir, f"{sid}_frames")
    os.makedirs(frames_dir, exist_ok=True)

    frame_count = 0
    while True:
        # Read a frame from the video
        ret, frame = cap.read()
        if not ret:
            break

        # Save the frame as an image
        frame_path = os.path.join(frames_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_count += 1

    print(f"Extracted {frame_count} frames from {video_file}")
    cap.release()

# async def concatenate_and_convert(sid):
#     client_file_path = os.path.join(output_dir, f"{sid}.webm")
#     output_file_path = os.path.join(output_dir, f"{sid}.mp4")
    
#     if os.path.exists(client_file_path):
#         try:
#             # Convert WebM to MP4 using ffmpeg
#             stream = ffmpeg.input(client_file_path)
#             stream = ffmpeg.output(stream, output_file_path,y=None)
#             ffmpeg.run(stream)
#             print(f"File saved as {output_file_path}")
#         except ffmpeg.Error as e:
#             print(f"Error during conversion: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(sio_app, host="0.0.0.0", port=8000)
