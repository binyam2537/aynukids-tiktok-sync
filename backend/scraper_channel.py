import time
import random
import logging
from typing import List, Dict, Any

from config import TIKTOK_HANDLE, MAX_VIDEOS_PER_RUN, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, CHANNEL_PROVIDER
from db import db
from providers.ytdlp_provider import YTDLPProvider
from providers.oembed_provider import OEmbedProvider

logger = logging.getLogger("aynukids.scraper_channel")

def get_channel_provider():
    if CHANNEL_PROVIDER.lower() == "ytdlp":
        return YTDLPProvider()
    else:
        # Easy to add ApifyProvider() here later
        logger.warning(f"Unknown provider {CHANNEL_PROVIDER}, falling back to ytdlp")
        return YTDLPProvider()

def run_stream_a() -> Dict[str, Any]:
    """
    Stream A: Scrape channel videos and enrich with oEmbed.
    Returns statistics about the run.
    """
    logger.info("Starting Stream A: Channel Video Collection")
    start_time = time.time()
    stats = {"stream": "channel", "status": "failed", "videos_found": 0, "videos_new": 0, "error_message": None}
    
    try:
        provider = get_channel_provider()
        videos = provider.get_channel_videos(TIKTOK_HANDLE, MAX_VIDEOS_PER_RUN)
        stats["videos_found"] = len(videos)
        
        if not videos:
            logger.warning("No videos found for channel.")
            stats["status"] = "success"
            return stats

        existing_ids = db.get_existing_video_ids()

        for video in videos:
            if str(video["id"]) in existing_ids:
                # Skip already processed videos to speed up the run
                continue

            # Add randomized delay between oEmbed requests to be polite
            delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
            time.sleep(delay)
            
            # Enrich with oEmbed data
            oembed_data = OEmbedProvider.get_metadata(video["video_url"])
            if oembed_data:
                video["title"] = oembed_data["title"]
                video["thumbnail_url"] = oembed_data["thumbnail_url"]
                video["embed_html"] = oembed_data["embed_html"]
                video["author_name"] = oembed_data["author_name"]
                
                # Try to extract sound_id from embed HTML if yt-dlp missed it
                if not video.get("sound_id") and video.get("embed_html"):
                    import re
                    match = re.search(r'music/.*?-(?P<sound_id>\d+)', video["embed_html"])
                    if match:
                        video["sound_id"] = match.group("sound_id")
                        logger.info(f"Extracted sound_id {video['sound_id']} from oEmbed HTML")
            
            # Save sound to db if discovered
            if video.get("sound_id"):
                sound_data = {
                    "id": video["sound_id"],
                    "title": f"Sound {video['sound_id']} from {TIKTOK_HANDLE}", # Will be updated if we fetch sound details
                    "origin_video_id": video["id"],
                    "music_url": f"https://www.tiktok.com/music/sound-{video['sound_id']}"
                }
                db.upsert_sound(sound_data)
                
            # Upsert video
            db.upsert_video(video)
            stats["videos_new"] += 1
            
        stats["status"] = "success"
        
    except Exception as e:
        logger.exception("Error in Stream A")
        stats["error_message"] = str(e)
        
    finally:
        duration = time.time() - start_time
        db.log_sync_run(
            stream=stats["stream"],
            status=stats["status"],
            videos_found=stats["videos_found"],
            videos_new=stats["videos_new"],
            duration=duration,
            error_msg=stats["error_message"]
        )
        logger.info(f"Stream A finished in {duration:.2f}s with status {stats['status']}")
        
    return stats

if __name__ == "__main__":
    run_stream_a()
