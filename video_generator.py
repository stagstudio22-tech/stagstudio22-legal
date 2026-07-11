import os
from gtts import gTTS

try:
    from moviepy import TextClip, ColorClip, AudioFileClip, CompositeVideoClip
except ImportError:
    from moviepy.editor import TextClip, ColorClip, AudioFileClip, CompositeVideoClip

class VideoGenerator:
    """
    A class to generate videos with text, audio, and basic overlays using gTTS and MoviePy.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_speech(self, text: str, filename: str = "narration.mp3") -> str:
        """
        Generates text-to-speech audio file using gTTS.

        :param text: Text to read aloud.
        :param filename: Filename for the generated audio.
        :return: Absolute path to the generated audio file.
        """
        filepath = os.path.join(self.output_dir, filename)
        tts = gTTS(text=text, lang="en")
        tts.save(filepath)
        return filepath

    def create_video_from_text(self, text_segments: list, audio_filepath: str, output_filename: str = "output_video.mp4", duration: float = None, fps: int = 24, resolution: tuple = (1280, 720)) -> str:
        """
        Creates a video by combining a background color clip, text overlays, and an audio narration.

        :param text_segments: List of tuples/dicts with {"text": str, "start": float, "end": float} for timing.
        :param audio_filepath: Path to the narration audio clip.
        :param output_filename: Path or name for the final video file.
        :param duration: Total duration of the video. If None, it uses the duration of the audio.
        :param fps: Frames per second.
        :param resolution: Video resolution (width, height).
        :return: Path to the generated video.
        """
        video_filepath = os.path.join(self.output_dir, output_filename)

        # Load audio clip
        audio_clip = AudioFileClip(audio_filepath)
        if duration is None:
            duration = audio_clip.duration

        # Create a background clip (solid dark grey/blue color)
        bg_clip = ColorClip(size=resolution, color=(30, 41, 59), duration=duration)

        clips = [bg_clip]

        # Use an available system font family with file extension that pillow/freetype can find automatically
        font_family = "LiberationSans-Regular"

        # Add text overlays at specified intervals
        for segment in text_segments:
            text = segment.get("text", "")
            start = segment.get("start", 0.0)
            end = segment.get("end", duration)

            # Create a simple clean text overlay
            # Note: In MoviePy v2, first positional argument is font (or we can use keyword-only).
            # We specify text explicitly as text=text, and font as font="LiberationSans-Regular" to be fully compatible.
            try:
                txt_clip = TextClip(
                    text=text,
                    font_size=48,
                    color='white',
                    font=font_family,
                    size=(resolution[0] - 100, None),
                    method='caption'
                )
                # In MoviePy v2.x, set_start/set_end are renamed to with_start/with_end/with_position/with_duration
                txt_clip = txt_clip.with_start(start).with_end(end).with_position('center')
            except (TypeError, AttributeError):
                # Fallback for old MoviePy versions (v1.x)
                txt_clip = TextClip(
                    text,
                    fontsize=48,
                    color='white',
                    font=font_family,
                    size=(resolution[0] - 100, None),
                    method='caption'
                )
                txt_clip = txt_clip.set_start(start).set_end(end).set_position('center')
            clips.append(txt_clip)

        # Composite everything together
        video = CompositeVideoClip(clips, size=resolution)
        video = video.with_audio(audio_clip) if hasattr(video, "with_audio") else video.set_audio(audio_clip)

        # Write the video file
        # Using libx264 for high compatibility, and aac for audio format
        video.write_videofile(
            video_filepath,
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(self.output_dir, "temp-audio.m4a"),
            remove_temp=True
        )

        # Close clips to release resources
        video.close()
        audio_clip.close()
        bg_clip.close()

        return video_filepath

if __name__ == "__main__":
    # Simple test run
    print("Testing VideoGenerator...")
    try:
        generator = VideoGenerator()
        text = "Hello and welcome! This video was automatically generated using Python, MoviePy, and Google Text to Speech."

        print("Generating audio narration...")
        audio_path = generator.generate_speech(text)

        segments = [
            {"text": "Hello and welcome!", "start": 0.0, "end": 2.0},
            {"text": "This video was automatically generated using Python, MoviePy, and Google Text to Speech.", "start": 2.0, "end": 7.0}
        ]

        print("Generating final video...")
        video_path = generator.create_video_from_text(segments, audio_path, duration=7.0)
        print(f"Video generated successfully at: {video_path}")
    except Exception as e:
        print(f"Error: {e}")
