# Automated YouTube Workflow

An automated workflow that scans YouTube for highly viewed videos in a specified niche, generates a video inspired by them using Text-to-Speech narration with text captions, and automatically uploads the result to your YouTube Channel.

## Core Features
1. **Niche Scanner (`youtube_scanner.py`)**: Interacts with the YouTube Data API v3 to search for popular videos and extract statistics (views, likes, comments).
2. **Video Generator (`video_generator.py`)**: Utilizes Google Text-to-Speech (gTTS) to create narration, and compiles color backdrops, text captions, and audio into a high-quality video using MoviePy.
3. **YouTube Uploader (`youtube_uploader.py`)**: Authenticates via Google OAuth 2.0 and securely uploads the final MP4 video as public, private, or unlisted.
4. **Orchestrator (`main_workflow.py`)**: Main entry point connecting the scanning, generation, and uploading modules together.

## Requirements & Prerequisites
Before running the workflow, make sure you have python installed along with the following:
* **System Dependencies**:
  * **FFmpeg**: Required by MoviePy.
  * **ImageMagick**: Required by MoviePy for rendering `TextClip` captions on top of background visuals.
* **Python libraries**: Install via `pip install -r requirements.txt`

## Google API Credentials & Configuration
To use this tool, you must configure two credential files in the root folder:

1. **YOUTUBE_API_KEY**: Export your YouTube API Key to your environment variables to allow scanning:
   ```bash
   export YOUTUBE_API_KEY="your-api-key-here"
   ```
2. **client_secrets.json**: Download OAuth 2.0 Client ID Credentials from your Google Cloud Console for YouTube Uploads and save them to the project root directory as `client_secrets.json`.

## Quick Start / Usage

To perform a test run that scans YouTube and generates a video without uploading it:
```bash
python main_workflow.py --query "Python Programming" --skip-upload --max-results 5
```

To run the complete automated workflow including upload to your channel (defaults to private):
```bash
python main_workflow.py --query "Cooking Hacks" --max-results 5 --privacy private
```

## Running Tests
To run the automated test suite, execute:
```bash
pytest test_workflow.py
```
