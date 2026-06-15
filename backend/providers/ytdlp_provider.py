import json
import subprocess
import logging
from typing import List, Dict, Any
from .base import ChannelProvider, SoundProvider

logger = logging.getLogger("aynukids.ytdlp")

class YTDLPProvider(ChannelProvider, SoundProvider):
    """
    Implementation of scraping using yt-dlp --dump-json.
    """
    
    def get_channel_videos(self, handle: str, max_videos: int = 0) -> List[Dict[str, Any]]:
        url = f"https://www.tiktok.com/@{handle}"
        logger.info(f"Running yt-dlp for channel: {url}")
        
        cmd = ["yt-dlp", "--flat-playlist", "-J", url]
        if max_videos > 0:
             cmd.extend(["--max-downloads", str(max_videos)])
             
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            videos = []
            
            # yt-dlp -J with --flat-playlist outputs one JSON object per line for the playlist entries,
            # or a single JSON object containing 'entries'. Let's handle both.
            
            try:
                # Try parsing as a single JSON object
                data = json.loads(result.stdout)
                if "entries" in data:
                    entries = data["entries"]
                else:
                    entries = [data]
            except json.JSONDecodeError:
                # Try parsing line by line
                entries = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        entries.append(json.loads(line))
            
            for entry in entries:
                # Some entries might just be references, ensure we have an id and url
                video_id = entry.get("id")
                video_url = entry.get("url") or entry.get("webpage_url")
                
                if not video_url and video_id:
                     video_url = f"https://www.tiktok.com/@{handle}/video/{video_id}"
                     
                if video_id and video_url:
                    # Try to extract sound ID if available in this flat representation
                    sound_id = None
                    if "track_id" in entry:
                         sound_id = entry["track_id"]
                    
                    videos.append({
                        "id": video_id,
                        "video_url": video_url,
                        "sound_id": sound_id,
                        # Pass along raw title if available, but oEmbed will enrich later
                        "title": entry.get("title", ""), 
                        "author_name": entry.get("uploader", handle)
                    })
            
            logger.info(f"Found {len(videos)} videos via yt-dlp for {handle}")
            return videos
            
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp command failed: {e.stderr}")
            # If yt-dlp fails completely, return empty list (we can add fallbacks later)
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing yt-dlp output: {e}")
            return []

    def get_videos_by_sound(self, sound_id: str, max_videos: int = 0) -> List[Dict[str, Any]]:
        """
        Note: yt-dlp does not officially support scraping TikTok sound pages directly well.
        This is a best-effort implementation that might fail or return limited results.
        If it fails consistently, you will need to switch to Apify or another provider for SoundProvider.
        """
        url = f"https://www.tiktok.com/music/sound-{sound_id}"
        logger.info(f"Running yt-dlp for sound page: {url}")
        
        cmd = ["yt-dlp", "--flat-playlist", "-J", url]
        if max_videos > 0:
             cmd.extend(["--max-downloads", str(max_videos)])
             
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            videos = []
            
            try:
                data = json.loads(result.stdout)
                if "entries" in data:
                    entries = data["entries"]
                else:
                    entries = [data]
            except json.JSONDecodeError:
                entries = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        entries.append(json.loads(line))
            
            for entry in entries:
                video_id = entry.get("id")
                video_url = entry.get("url") or entry.get("webpage_url")
                
                if video_id and video_url:
                    videos.append({
                        "id": video_id,
                        "video_url": video_url,
                        "sound_id": sound_id,
                        "title": entry.get("title", ""),
                        "creator_handle": entry.get("uploader", "unknown"),
                        "creator_name": entry.get("uploader", "unknown")
                    })
            
            logger.info(f"Found {len(videos)} videos via yt-dlp for sound {sound_id}")
            return videos
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"yt-dlp command failed for sound {sound_id}. yt-dlp often struggles with sound pages. Error: {e.stderr}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing yt-dlp output for sound: {e}")
            return []
