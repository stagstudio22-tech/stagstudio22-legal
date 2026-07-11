import os
import argparse
import json
from youtube_scanner import YouTubeScanner
from video_generator import VideoGenerator
from youtube_uploader import YouTubeUploader

def run_workflow(query: str, max_scan_results: int, output_dir: str, skip_upload: bool, upload_privacy: str):
    print("=== Starting Automated YouTube Workflow ===")

    # Step 1: Scan YouTube for popular videos in this niche
    print(f"\n[Step 1] Scanning YouTube for niche: '{query}'...")
    scanner = YouTubeScanner()
    try:
        videos = scanner.scan_high_view_videos(query, max_results=max_scan_results)
        print(f"Found {len(videos)} highly viewed videos in this niche.")
        if not videos:
            print("No videos found. Exiting.")
            return

        # Display top 3
        for idx, video in enumerate(videos[:3]):
            print(f"  {idx+1}. {video['title']} ({video['view_count']:,} views)")
    except Exception as e:
        print(f"Error scanning YouTube: {e}")
        print("Ensure you have set the YOUTUBE_API_KEY environment variable.")
        return

    # Step 2: Use metadata from the top video to generate or inspire new script content
    top_video = videos[0]
    print(f"\n[Step 2] Selecting top video as inspiration: '{top_video['title']}'")

    # We will generate a video response, outline, or review based on the top video
    script_text = (
        f"Today we are exploring a highly trending topic on YouTube: {top_video['title']}. "
        f"This subject has gained massive popularity recently, and we are breaking down why it matters. "
        f"Let us jump into the details and look at what makes this so engaging for viewers."
    )

    segments = [
        {"text": f"Today we are exploring a highly trending topic on YouTube: {top_video['title'][:50]}...", "start": 0.0, "end": 4.0},
        {"text": "This subject has gained massive popularity recently, and we are breaking down why it matters.", "start": 4.0, "end": 8.0},
        {"text": "Let us jump into the details and look at what makes this so engaging for viewers.", "start": 8.0, "end": 12.0}
    ]

    # Step 3: Generate the Video & Audio narration
    print("\n[Step 3] Generating video and narration audio...")
    generator = VideoGenerator(output_dir=output_dir)
    try:
        audio_path = generator.generate_speech(script_text, filename="workflow_narration.mp3")
        video_path = generator.create_video_from_text(
            text_segments=segments,
            audio_filepath=audio_path,
            output_filename="workflow_video.mp4",
            duration=12.0
        )
        print(f"Video generated successfully at: {video_path}")
    except Exception as e:
        print(f"Error generating video: {e}")
        return

    # Step 4: Upload to YouTube channel
    if skip_upload:
        print("\n[Step 4] Skipping upload as requested by user (--skip-upload).")
        return

    print("\n[Step 4] Uploading video to your YouTube Channel...")
    uploader = YouTubeUploader()
    try:
        uploader.authenticate()

        # Generate appropriate meta details
        video_title = f"Trending: {top_video['title']}"
        if len(video_title) > 90:
            video_title = video_title[:90] + "..."

        video_description = (
            f"An analysis and discussion inspired by the trending video: {top_video['title']}.\n\n"
            f"Original Video: {top_video['url']}\n"
            f"Automatically generated with StagStudio22 Workflow."
        )

        video_id = uploader.upload_video(
            file_path=video_path,
            title=video_title,
            description=video_description,
            tags=[query, "trending", "automated"],
            privacy_status=upload_privacy
        )
        print(f"Successfully uploaded! Video ID: {video_id}")
    except Exception as e:
        print(f"Error uploading video: {e}")
        print("Note: To upload, make sure client_secrets.json is present and configured correctly.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated YouTube Workflow: Scan, Generate, and Upload Videos.")
    parser.add_argument("--query", type=str, default="Python programming", help="Search niche query to scan for popular videos.")
    parser.add_argument("--max-results", type=int, default=5, help="Number of search results to fetch.")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory where temporary and final video/audio assets are stored.")
    parser.add_argument("--skip-upload", action="store_true", help="Set to True if you only want to scan and generate video without uploading.")
    parser.add_argument("--privacy", type=str, default="private", choices=["private", "unlisted", "public"], help="Privacy status of the uploaded video.")

    args = parser.parse_args()
    run_workflow(
        query=args.query,
        max_scan_results=args.max_results,
        output_dir=args.output_dir,
        skip_upload=args.skip_upload,
        upload_privacy=args.privacy
    )
