import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    """
    A class to authenticate and upload videos to YouTube using YouTube Data API v3 and OAuth 2.0.
    """
    # YouTube Upload OAuth Scope
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self, client_secrets_file: str = "client_secrets.json", token_file: str = "token.json"):
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.youtube = None

    def authenticate(self):
        """
        Loads cached tokens or initiates the OAuth flow to authenticate the user.
        """
        creds = None
        # Load credentials if they exist
        if os.path.exists(self.token_file):
            import json
            try:
                with open(self.token_file, "r") as f:
                    creds_data = json.load(f)
                creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_data, self.SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")

        # If there are no valid credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh credentials: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.client_secrets_file):
                    raise FileNotFoundError(
                        f"Client secrets file '{self.client_secrets_file}' not found. "
                        "Please download it from the Google Cloud Console and place it in the workspace."
                    )
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        self.youtube = build("youtube", "v3", credentials=creds)

    def upload_video(self, file_path: str, title: str, description: str, category_id: str = "22", tags: list = None, privacy_status: str = "private") -> str:
        """
        Uploads a video to YouTube.

        :param file_path: Path to the video file to upload.
        :param title: Video title (max 100 characters).
        :param description: Video description.
        :param category_id: YouTube video category ID (e.g., '22' is People & Blogs, '27' is Education, '28' is Science & Technology).
        :param tags: List of tags/keywords.
        :param privacy_status: Privacy status ('public', 'private', or 'unlisted').
        :return: Video ID of the uploaded video.
        """
        if not self.youtube:
            raise ValueError("Uploader is not authenticated. Call authenticate() before uploading.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found at: {file_path}")

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags or [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        # MediaFileUpload chunksize can be customized. Using 1MB chunks.
        media = MediaFileUpload(
            file_path,
            mimetype="video/*",
            resumable=True,
            chunksize=1024 * 1024
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        print(f"Uploading '{file_path}' to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%...")

        video_id = response.get("id")
        print(f"Upload complete! Video ID: {video_id}")
        return video_id

if __name__ == "__main__":
    # Test block
    print("Testing YouTubeUploader module structure...")
    uploader = YouTubeUploader()
    # To run authentications, user must configure client_secrets.json.
