import unittest
from unittest.mock import MagicMock, patch
from youtube_scanner import YouTubeScanner
from video_generator import VideoGenerator
from youtube_uploader import YouTubeUploader

class TestYouTubeScanner(unittest.TestCase):
    @patch("youtube_scanner.build")
    def test_scan_high_view_videos(self, mock_build):
        # Setup mocks
        mock_youtube_client = MagicMock()
        mock_build.return_value = mock_youtube_client

        # Mocking the search.list chain
        mock_search = MagicMock()
        mock_youtube_client.search.return_value = mock_search
        mock_search_list = MagicMock()
        mock_search.list.return_value = mock_search_list
        mock_search_list.execute.return_value = {
            "items": [
                {"id": {"videoId": "test_id_1"}},
                {"id": {"videoId": "test_id_2"}}
            ]
        }

        # Mocking the videos.list chain
        mock_videos = MagicMock()
        mock_youtube_client.videos.return_value = mock_videos
        mock_videos_list = MagicMock()
        mock_videos.list.return_value = mock_videos_list
        mock_videos_list.execute.return_value = {
            "items": [
                {
                    "id": "test_id_1",
                    "snippet": {
                        "title": "Popular Video 1",
                        "description": "First description",
                        "channelTitle": "Test Channel 1",
                        "publishedAt": "2023-11-01T12:00:00Z"
                    },
                    "statistics": {
                        "viewCount": "1500000",
                        "likeCount": "50000",
                        "commentCount": "3000"
                    }
                },
                {
                    "id": "test_id_2",
                    "snippet": {
                        "title": "Popular Video 2",
                        "description": "Second description",
                        "channelTitle": "Test Channel 2",
                        "publishedAt": "2023-11-02T12:00:00Z"
                    },
                    "statistics": {
                        "viewCount": "2500000",
                        "likeCount": "80000",
                        "commentCount": "6000"
                    }
                }
            ]
        }

        scanner = YouTubeScanner(api_key="mock_key")
        videos = scanner.scan_high_view_videos(query="test query")

        # Verify result sorted by viewCount (test_id_2 has 2.5M, test_id_1 has 1.5M)
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]["video_id"], "test_id_2")
        self.assertEqual(videos[0]["view_count"], 2500000)
        self.assertEqual(videos[1]["video_id"], "test_id_1")
        self.assertEqual(videos[1]["view_count"], 1500000)

    def test_get_published_after_date(self):
        scanner = YouTubeScanner(api_key="mock_key")
        date_str = scanner.get_published_after_date(days=7)
        self.assertTrue(date_str.endswith("Z"))
        self.assertEqual(len(date_str), 20)

class TestVideoGenerator(unittest.TestCase):
    @patch("video_generator.gTTS")
    def test_generate_speech(self, mock_gTTS):
        mock_tts_instance = MagicMock()
        mock_gTTS.return_value = mock_tts_instance

        generator = VideoGenerator(output_dir="test_output")
        filepath = generator.generate_speech("Test text to say", filename="test_narration.mp3")

        mock_gTTS.assert_called_once_with(text="Test text to say", lang="en")
        mock_tts_instance.save.assert_called_once_with(filepath)
        self.assertTrue(filepath.endswith("test_narration.mp3"))

class TestYouTubeUploader(unittest.TestCase):
    @patch("youtube_uploader.build")
    @patch("youtube_uploader.MediaFileUpload")
    @patch("youtube_uploader.os.path.exists")
    def test_upload_video(self, mock_exists, mock_media_file_upload, mock_build):
        # Setup mocks
        mock_exists.return_value = True
        mock_youtube_client = MagicMock()
        mock_build.return_value = mock_youtube_client

        mock_videos = MagicMock()
        mock_youtube_client.videos.return_value = mock_videos
        mock_insert = MagicMock()
        mock_videos.insert.return_value = mock_insert

        # Mock resumable media upload next_chunk responses
        mock_insert.next_chunk.side_effect = [
            (MagicMock(progress=lambda: 0.5), None),
            (MagicMock(progress=lambda: 1.0), {"id": "uploaded_video_id"})
        ]

        uploader = YouTubeUploader()
        uploader.youtube = mock_youtube_client

        video_id = uploader.upload_video(
            file_path="mock_video.mp4",
            title="My Great Title",
            description="My Great Description",
            tags=["tag1", "tag2"],
            privacy_status="private"
        )

        self.assertEqual(video_id, "uploaded_video_id")

if __name__ == "__main__":
    unittest.main()
