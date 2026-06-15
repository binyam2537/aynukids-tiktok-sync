from typing import Any, Dict, List, Optional
from supabase import create_client, Client
import logging

from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

logger = logging.getLogger("aynukids.db")

class Database:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    def upsert_video(self, video_data: Dict[str, Any]) -> None:
        """Upsert a video into the 'videos' table."""
        try:
            response = self.client.table("videos").upsert(video_data).execute()
            logger.debug(f"Upserted video {video_data.get('id')}: {response.data}")
        except Exception as e:
            logger.error(f"Failed to upsert video {video_data.get('id')}: {e}")
            raise

    def upsert_sound(self, sound_data: Dict[str, Any]) -> None:
        """Upsert a sound into the 'sounds' table."""
        try:
            response = self.client.table("sounds").upsert(sound_data).execute()
            logger.debug(f"Upserted sound {sound_data.get('id')}: {response.data}")
        except Exception as e:
            logger.error(f"Failed to upsert sound {sound_data.get('id')}: {e}")
            raise

    def get_all_active_sounds(self) -> List[Dict[str, Any]]:
        """Get all sounds that are marked as active."""
        try:
            response = self.client.table("sounds").select("*").eq("is_active", True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch active sounds: {e}")
            raise

    def get_existing_video_ids(self) -> set:
        """Get a set of all video IDs currently in the database to avoid re-fetching."""
        try:
            response = self.client.table("videos").select("id").execute()
            return {item["id"] for item in response.data}
        except Exception as e:
            logger.error(f"Failed to fetch existing video IDs: {e}")
            return set()

    def get_existing_community_video_ids(self) -> set:
        """Get a set of all community video IDs currently in the database."""
        try:
            response = self.client.table("community_videos").select("id").execute()
            return {item["id"] for item in response.data}
        except Exception as e:
            logger.error(f"Failed to fetch existing community video IDs: {e}")
            return set()

    def upsert_community_video(self, video_data: Dict[str, Any]) -> None:
        """Upsert a community video. Does not overwrite approval_status if it already exists."""
        try:
            # First, check if the video exists to avoid overwriting approval_status
            existing = self.client.table("community_videos").select("approval_status").eq("id", video_data["id"]).execute()
            if existing.data:
                # Video exists, don't update approval_status or reviewed fields
                video_data.pop("approval_status", None)
                video_data.pop("reviewed_by", None)
                video_data.pop("reviewed_at", None)
            
            response = self.client.table("community_videos").upsert(video_data).execute()
            logger.debug(f"Upserted community video {video_data.get('id')}: {response.data}")
        except Exception as e:
            logger.error(f"Failed to upsert community video {video_data.get('id')}: {e}")
            raise

    def log_sync_run(self, stream: str, status: str, videos_found: int, videos_new: int, duration: float, error_msg: Optional[str] = None) -> None:
        """Log a synchronization run."""
        try:
            log_data = {
                "stream": stream,
                "status": status,
                "videos_found": videos_found,
                "videos_new": videos_new,
                "duration_seconds": duration,
                "error_message": error_msg
            }
            self.client.table("sync_log").insert(log_data).execute()
            logger.info(f"Logged sync run for {stream} with status {status}")
        except Exception as e:
            logger.error(f"Failed to log sync run: {e}")
            # Don't raise here, failing to log shouldn't crash the pipeline

db = Database()
