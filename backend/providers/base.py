from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ChannelProvider(ABC):
    """Abstract base class for scraping videos from a TikTok channel."""
    
    @abstractmethod
    def get_channel_videos(self, handle: str, max_videos: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch a list of videos for a given TikTok handle.
        Returns a list of dictionaries, where each dict contains basic video metadata
        (at minimum: 'id', 'video_url', 'sound_id' if possible).
        """
        pass

class SoundProvider(ABC):
    """Abstract base class for scraping videos that use a specific sound."""
    
    @abstractmethod
    def get_videos_by_sound(self, sound_id: str, max_videos: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch a list of videos that use the given sound_id.
        Returns a list of dictionaries containing video metadata.
        """
        pass
