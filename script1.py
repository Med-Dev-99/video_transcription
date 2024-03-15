import argparse
from moviepy.editor import VideoFileClip
from datetime import timedelta
import whisper
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the Whisper model outside the function
model = whisper.load_model("base")
logging.info("Whisper model loaded.")

def transcribe_audio(audio_path, srt_filename):
    transcribe = model.transcribe(audio=audio_path)
    segments = transcribe['segments']

    with open(srt_filename, 'a', encoding='utf-8') as srtFile:
        for segment in segments:
            startTime = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
            endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
            text = segment['text']
            segmentId = segment['id'] + 1
            segment_srt = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
            srtFile.write(segment_srt)

def process_video(video_path):
    try:
        video = VideoFileClip(video_path)
        audio_path = video_path + '.mp3'
        video.audio.write_audiofile(audio_path)

        srt_path = os.path.splitext(video_path)[0] + '.srt'
        logging.info(f"Processing video: {video_path}")

        transcribe_audio(audio_path, srt_path)
        logging.info(f"Generated subtitles for {video_path}")

    except Exception as e:
        logging.error(f"Error processing {video_path}: {e}")

def process_directory(directory_path):
    srt_folder = os.path.join(directory_path, 'SrtFiles')
    if not os.path.exists(srt_folder):
        os.makedirs(srt_folder)

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.mp4'):
                video_path = os.path.join(root, file)
                process_video(video_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate subtitles for videos in a folder.")
    parser.add_argument("folder", help="Path to the folder containing video files")
    args = parser.parse_args()

    process_directory(args.folder)
