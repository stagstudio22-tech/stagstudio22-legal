import os
import sys
import json
import queue
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response, send_from_directory

# Configure system-wide stdout capture before importing any module
class ThreadSafeLogStream:
    def __init__(self):
        self.queues = []
        self.history = []
        self.lock = threading.Lock()

    def register(self):
        with self.lock:
            q = queue.Queue()
            self.queues.append(q)
            return q

    def unregister(self, q):
        with self.lock:
            if q in self.queues:
                self.queues.remove(q)

    def write(self, data):
        if not data:
            return
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='replace')
        sys.__stdout__.write(data)
        with self.lock:
            self.history.append(data)
            if len(self.history) > 1000:
                self.history.pop(0)
            for q in list(self.queues):
                q.put(data)

    def flush(self):
        sys.__stdout__.flush()

# Redirect stdout and stderr
log_stream = ThreadSafeLogStream()
sys.stdout = log_stream
sys.stderr = log_stream

# Import the workflow components safely
from youtube_scanner import YouTubeScanner
from video_generator import VideoGenerator
from youtube_uploader import YouTubeUploader
from main_workflow import run_workflow_once

app = Flask(__name__)

# Global shared state
global_state = {
    "is_running": False,
    "current_task": "Idle",
    "scanned_videos": [],
    "generated_video_path": None,
    "generated_audio_path": None,
    "last_run_time": None,
    "last_run_status": None,
}
state_lock = threading.Lock()

# Wrap original components to capture live telemetry
original_scan = YouTubeScanner.scan_high_view_videos
def wrapped_scan(self, *args, **kwargs):
    results = original_scan(self, *args, **kwargs)
    with state_lock:
        global_state["scanned_videos"] = results
    return results
YouTubeScanner.scan_high_view_videos = wrapped_scan

original_create_video = VideoGenerator.create_video_from_text
def wrapped_create_video(self, *args, **kwargs):
    path = original_create_video(self, *args, **kwargs)
    with state_lock:
        global_state["generated_video_path"] = path
    return path
VideoGenerator.create_video_from_text = wrapped_create_video

original_generate_speech = VideoGenerator.generate_speech
def wrapped_generate_speech(self, *args, **kwargs):
    path = original_generate_speech(self, *args, **kwargs)
    with state_lock:
        global_state["generated_audio_path"] = path
    return path
VideoGenerator.generate_speech = wrapped_generate_speech


def execute_task_thread(task_type, params):
    with state_lock:
        global_state["is_running"] = True
        global_state["current_task"] = task_type
        global_state["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        global_state["last_run_status"] = f"Running: {task_type}"

    try:
        if task_type == "Full Workflow":
            print(f"[*] Starting full workflow cycle for query: '{params['query']}'")
            success = run_workflow_once(
                query=params["query"],
                max_scan_results=params["max_results"],
                output_dir=params["output_dir"],
                skip_upload=params["skip_upload"],
                upload_privacy=params["privacy"],
                within_days=params["within_days"]
            )
            with state_lock:
                global_state["last_run_status"] = "Success" if success else "Failed (Check terminal logs)"

        elif task_type == "Scan Only":
            print(f"[*] Starting search scanner for query: '{params['query']}'")
            scanner = YouTubeScanner()
            videos = scanner.scan_high_view_videos(
                query=params["query"],
                max_results=params["max_results"],
                within_days=params["within_days"]
            )
            print(f"[+] Scan completed. Found {len(videos)} highly-viewed videos.")
            with state_lock:
                global_state["scanned_videos"] = videos
                global_state["last_run_status"] = f"Completed scanner scan. Found {len(videos)} videos."

        elif task_type == "Generate Video":
            print("[*] Launching video generation suite...")
            generator = VideoGenerator(output_dir=params["output_dir"])
            script = params["script_text"]

            # Simple automatic segment splitting
            print("[*] Processing script narration audio...")
            audio_path = generator.generate_speech(script, filename="custom_narration.mp3")

            # Divide script into 3 equal text segments for visual timing
            sentences = [s.strip() for s in script.split(".") if s.strip()]
            if not sentences:
                sentences = [script]

            segment_duration = 12.0 / max(len(sentences), 1)
            segments = []
            for i, sent in enumerate(sentences):
                segments.append({
                    "text": sent,
                    "start": i * segment_duration,
                    "end": (i + 1) * segment_duration
                })

            print("[*] Designing visual MP4 video with LiberationSans typography...")
            video_path = generator.create_video_from_text(
                text_segments=segments,
                audio_filepath=audio_path,
                output_filename="custom_video.mp4",
                duration=12.0
            )
            print(f"[+] Video successfully compiled at: {video_path}")
            with state_lock:
                global_state["generated_video_path"] = video_path
                global_state["generated_audio_path"] = audio_path
                global_state["last_run_status"] = "Custom video & audio assets generated successfully."

        elif task_type == "Upload Video":
            print(f"[*] Authenticating and uploading local asset: {params['file_path']}")
            uploader = YouTubeUploader()
            uploader.authenticate()
            video_id = uploader.upload_video(
                file_path=params["file_path"],
                title=params["title"],
                description=params["description"],
                tags=params["tags"],
                privacy_status=params["privacy"]
            )
            print(f"[+] Direct Upload completed successfully! Video ID: {video_id}")
            with state_lock:
                global_state["last_run_status"] = f"Video successfully uploaded. ID: {video_id}"

    except Exception as e:
        print(f"[!] Engine execution error: {e}")
        with state_lock:
            global_state["last_run_status"] = f"Error: {str(e)}"
    finally:
        with state_lock:
            global_state["is_running"] = False
            global_state["current_task"] = "Idle"
        print("[*] Task operation complete.")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    api_key_configured = bool(os.environ.get("YOUTUBE_API_KEY"))
    client_secrets_configured = os.path.exists("client_secrets.json")

    with state_lock:
        return jsonify({
            "is_running": global_state["is_running"],
            "current_task": global_state["current_task"],
            "last_run_time": global_state["last_run_time"],
            "last_run_status": global_state["last_run_status"],
            "has_video": bool(global_state["generated_video_path"] and os.path.exists(global_state["generated_video_path"])),
            "has_audio": bool(global_state["generated_audio_path"] and os.path.exists(global_state["generated_audio_path"])),
            "scanned_videos_count": len(global_state["scanned_videos"]),
            "api_key_configured": api_key_configured,
            "client_secrets_configured": client_secrets_configured
        })

@app.route("/api/scanned-videos")
def get_scanned_videos():
    with state_lock:
        return jsonify(global_state["scanned_videos"])

@app.route("/api/start", methods=["POST"])
def start_task():
    with state_lock:
        if global_state["is_running"]:
            return jsonify({"status": "error", "message": f"Engine is already running: {global_state['current_task']}"}), 400

    data = request.json or {}
    task_type = data.get("task", "Full Workflow")

    params = {}
    if task_type == "Full Workflow" or task_type == "Scan Only":
        params = {
            "query": data.get("query", "Python programming"),
            "max_results": int(data.get("max_results", 5)),
            "output_dir": data.get("output_dir", "output"),
            "skip_upload": bool(data.get("skip_upload", True)),
            "privacy": data.get("privacy", "private"),
            "within_days": int(data.get("within_days")) if data.get("within_days") else None
        }
    elif task_type == "Generate Video":
        params = {
            "script_text": data.get("script_text", "Automated premium script generation standard."),
            "output_dir": data.get("output_dir", "output")
        }
    elif task_type == "Upload Video":
        params = {
            "file_path": data.get("file_path", "output/workflow_video.mp4"),
            "title": data.get("title", "Premium Automated Video"),
            "description": data.get("description", "Uploaded via command center."),
            "tags": [t.strip() for t in data.get("tags", "trending, automation").split(",") if t.strip()],
            "privacy": data.get("privacy", "private")
        }

    # Run in a background thread
    t = threading.Thread(target=execute_task_thread, args=(task_type, params))
    t.daemon = True
    t.start()

    return jsonify({"status": "success", "message": f"Task '{task_type}' launched successfully."})

@app.route("/api/logs/stream")
def stream_logs():
    q = log_stream.register()

    def generate():
        with log_stream.lock:
            history_data = "".join(log_stream.history)
        if history_data:
            yield f"data: {json.dumps({'log': history_data})}\n\n"

        while True:
            try:
                log_chunk = q.get(timeout=15.0)
                yield f"data: {json.dumps({'log': log_chunk})}\n\n"
            except queue.Empty:
                yield "data: {}\n\n"
            except GeneratorExit:
                break
            except Exception:
                break

    response = Response(generate(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"

    @response.call_on_close
    def on_close():
        log_stream.unregister(q)

    return response

@app.route("/media/video")
def serve_video():
    with state_lock:
        path = global_state["generated_video_path"]
    if path and os.path.exists(path):
        return send_from_directory(os.path.dirname(path), os.path.basename(path))
    return "Video not found", 404

@app.route("/media/audio")
def serve_audio():
    with state_lock:
        path = global_state["generated_audio_path"]
    if path and os.path.exists(path):
        return send_from_directory(os.path.dirname(path), os.path.basename(path))
    return "Audio not found", 404

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
