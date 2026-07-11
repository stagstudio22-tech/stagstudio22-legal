import os
import sys
import time
import argparse
import json
from youtube_scanner import YouTubeScanner
from video_generator import VideoGenerator
from youtube_uploader import YouTubeUploader

def run_workflow_once(query: str, max_scan_results: int, output_dir: str, skip_upload: bool, upload_privacy: str, within_days: int) -> bool:
    """
    Executes a single cycle of: scanning, scripting, generation, and uploading.
    Returns True if a video was successfully found/created/uploaded, False otherwise.
    """
    print("\n--- Cycle Start ---")

    # Step 1: Scan YouTube for popular videos in this niche within the date range
    timeframe_str = f"published within the last {within_days} days" if within_days else "all-time"
    print(f"[Step 1] Scanning YouTube for niche '{query}' ({timeframe_str})...")
    scanner = YouTubeScanner()
    try:
        videos = scanner.scan_high_view_videos(query, max_results=max_scan_results, within_days=within_days)
        print(f"Found {len(videos)} highly viewed videos.")
        if not videos:
            print("No new popular videos found in this niche for the specified timeframe.")
            return False

        # Display top 3
        for idx, video in enumerate(videos[:3]):
            print(f"  {idx+1}. {video['title']} ({video['view_count']:,} views)")
    except Exception as e:
        print(f"Error scanning YouTube: {e}")
        print("Ensure you have set the YOUTUBE_API_KEY environment variable.")
        return False

    # Step 2: Use metadata from the top video to generate or inspire new script content
    top_video = videos[0]
    print(f"\n[Step 2] Selecting top video as inspiration: '{top_video['title']}'")

    # Clean up the title to avoid character encoding issues
    ascii_title = top_video['title'].encode('ascii', 'ignore').decode('ascii')

    script_text = (
        f"Today we are exploring a highly trending topic on YouTube: {ascii_title}. "
        f"This subject has gained massive popularity recently, and we are breaking down why it matters. "
        f"Let us jump into the details and look at what makes this so engaging for viewers."
    )

    segments = [
        {"text": f"Today we are exploring a highly trending topic: {ascii_title[:50]}...", "start": 0.0, "end": 4.0},
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
        return False

    # Step 4: Upload to YouTube channel
    if skip_upload:
        print("\n[Step 4] Skipping upload as requested by user (--skip-upload).")
        return True

    print("\n[Step 4] Uploading video to your YouTube Channel...")
    uploader = YouTubeUploader()
    try:
        uploader.authenticate()

        # Generate appropriate meta details
        video_title = f"Trending: {ascii_title}"
        if len(video_title) > 90:
            video_title = video_title[:90] + "..."

        video_description = (
            f"An analysis and discussion inspired by the trending video: {ascii_title}.\n\n"
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
        return True
    except Exception as e:
        print(f"Error uploading video: {e}")
        print("Note: To upload, make sure client_secrets.json is present and configured correctly.")
        return False

def run_workflow(query: str, max_scan_results: int, output_dir: str, skip_upload: bool, upload_privacy: str, within_days: int, loop: bool, interval_hours: float):
    print("=== Starting Automated YouTube Workflow ===")

    if not loop:
        run_workflow_once(query, max_scan_results, output_dir, skip_upload, upload_privacy, within_days)
        print("\n=== Workflow finished (Single Run) ===")
    else:
        print(f"Continuous Loop Mode Enabled! System will run every {interval_hours} hours.")
        try:
            while True:
                run_workflow_once(query, max_scan_results, output_dir, skip_upload, upload_privacy, within_days)

                print(f"\nCycle complete. Sleeping for {interval_hours} hours before scanning again...")
                # Sleep interval converted from hours to seconds
                time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            print("\nContinuous Loop mode terminated by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated YouTube Workflow: Scan, Generate, and Upload Videos.")
    parser.add_argument("--query", type=str, default="Python programming", help="Search niche query to scan for popular videos.")
    parser.add_argument("--max-results", type=int, default=5, help="Number of search results to fetch.")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory where temporary and final video/audio assets are stored.")
    parser.add_argument("--skip-upload", action="store_true", help="Set to True if you only want to scan and generate video without uploading.")
    parser.add_argument("--privacy", type=str, default="private", choices=["private", "unlisted", "public"], help="Privacy status of the uploaded video.")
    parser.add_argument("--within-days", type=int, default=None, help="Filter scanned videos published within the last N days (e.g. 1 for last 24h, 7 for last week).")
    parser.add_argument("--loop", action="store_true", help="Enable continuous loop mode to repeatedly run automation.")
    parser.add_argument("--interval", type=float, default=24.0, help="Interval in hours to sleep between loop cycles (default: 24 hours).")

    args = parser.parse_args()
    run_workflow(
        query=args.query,
        max_scan_results=args.max_results,
        output_dir=args.output_dir,
        skip_upload=args.skip_upload,
        upload_privacy=args.privacy,
        within_days=args.within_days,
        loop=args.loop,
        interval_hours=args.interval
    )
