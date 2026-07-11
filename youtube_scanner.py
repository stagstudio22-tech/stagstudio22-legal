import os
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

class YouTubeScanner:
    """
    A class to interact with the YouTube Data API v3 to scan for high-viewed videos.
    """
    def __init__(self, api_key: str = None):
        # Retrieve API Key from parameter or environment variable
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        self.youtube = None
        if self.api_key:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def get_published_after_date(self, days: int) -> str:
        """
        Calculates and formats the ISO 8601 (RFC 3339) datetime string for search.

        :param days: Number of days in the past (e.g. 1 for last 24h, 7 for last week).
        :return: ISO 8601 formatted datetime string (e.g. '2023-01-01T00:00:00Z').
        """
        past_date = datetime.now(timezone.utc) - timedelta(days=days)
        return past_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def scan_high_view_videos(self, query: str, max_results: int = 10, order: str = "viewCount", published_after: str = None, within_days: int = None):
        """
        Searches YouTube for videos matching a query, then fetches detailed statistics (like view count).

        :param query: Search query string.
        :param max_results: Number of search results to fetch (max 50).
        :param order: Method to order search results ('viewCount', 'date', 'relevance', etc.).
        :param published_after: ISO 8601 datetime string (e.g. '2023-01-01T00:00:00Z').
        :param within_days: Relative timeframe in days (e.g., 1 for last 24h, 7 for last week) - takes precedence over published_after.
        :return: List of dictionaries containing detailed video metadata.
        """
        if not self.youtube:
            raise ValueError("YouTube API key is missing. Please provide it or set the YOUTUBE_API_KEY environment variable.")

        # Step 1: Perform the search
        search_params = {
            "q": query,
            "part": "id,snippet",
            "type": "video",
            "order": order,
            "maxResults": min(max_results, 50)
        }

        if within_days is not None:
            search_params["publishedAfter"] = self.get_published_after_date(within_days)
        elif published_after:
            search_params["publishedAfter"] = published_after

        search_response = self.youtube.search().list(**search_params).execute()
        items = search_response.get("items", [])

        video_ids = [item["id"]["videoId"] for item in items if item.get("id", {}).get("videoId")]
        if not video_ids:
            return []

        # Step 2: Fetch detailed statistics for the identified videos
        videos_response = self.youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics"
        ).execute()

        results = []
        for item in videos_response.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})

            video_data = {
                "video_id": item.get("id"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "url": f"https://www.youtube.com/watch?v={item.get('id')}"
            }
            results.append(video_data)

        # Sort results by view count descending just in case search order wasn't strict
        results.sort(key=lambda x: x["view_count"], reverse=True)
        return results

if __name__ == "__main__":
    # Simple CLI test/demonstration
    import sys
    import json

    query = sys.argv[1] if len(sys.argv) > 1 else "Python programming"
    print(f"Scanning for high viewed videos with query: '{query}'...")

    try:
        scanner = YouTubeScanner()
        # Find videos published in the last 7 days
        videos = scanner.scan_high_view_videos(query, max_results=5, within_days=7)
        print(json.dumps(videos, indent=2))
    except Exception as e:
        print(f"Error during scan: {e}")
        print("Note: Make sure to set YOUTUBE_API_KEY environment variable to test locally.")
