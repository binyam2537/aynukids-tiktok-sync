import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("aynukids.oembed")

class OEmbedProvider:
    """
    Fetches rich metadata for a TikTok video using the official public oEmbed API.
    """
    
    BASE_URL = "https://www.tiktok.com/oembed"
    
    @classmethod
    def get_metadata(cls, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch oEmbed metadata for a given TikTok video URL.
        Returns a dictionary with title, author_name, thumbnail_url, embed_html.
        """
        params = {"url": video_url}
        logger.debug(f"Fetching oEmbed for: {video_url}")
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(cls.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "title": data.get("title", ""),
                    "author_name": data.get("author_name", ""),
                    "thumbnail_url": data.get("thumbnail_url", ""),
                    "embed_html": data.get("html", "")
                }
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} fetching oEmbed for {video_url}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching oEmbed for {video_url}: {e}")
            return None
