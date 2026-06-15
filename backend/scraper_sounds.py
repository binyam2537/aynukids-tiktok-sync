import time
import random
import logging
from typing import Dict, Any

from config import MAX_VIDEOS_PER_RUN, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, SOUND_PROVIDER
from db import db
from providers.ytdlp_provider import YTDLPProvider
from providers.oembed_provider import OEmbedProvider

logger = logging.getLogger("aynukids.scraper_sounds")

def get_sound_provider():
    if SOUND_PROVIDER.lower() == "ytdlp":
        return YTDLPProvider()
    else:
        # Easy to add ApifyProvider() here later
        logger.warning(f"Unknown provider {SOUND_PROVIDER}, falling back to ytdlp")
        return YTDLPProvider()

def run_stream_b() -> Dict[str, Any]:
    """
    Stream B: Discover fan videos that reuse our channel's sounds.
    Returns statistics about the run.
    """
    logger.info("Starting Stream B: Sound Repost Collection")
    start_time = time.time()
    stats = {"stream": "sounds", "status": "failed", "videos_found": 0, "videos_new": 0, "error_message": None}
    
    try:
        # Step 1: Get all active sounds from the DB
        active_sounds = db.get_all_active_sounds()
        logger.info(f"Found {len(active_sounds)} active sounds to track.")
        
        provider = get_sound_provider()
        
        for sound in active_sounds:
            sound_id = sound["id"]
            logger.info(f"Processing sound ID: {sound_id}")
            
            # Step 2: Fetch videos for this sound
            videos = provider.get_videos_by_sound(str(sound_id), MAX_VIDEOS_PER_RUN)
            stats["videos_found"] += len(videos)
            
            for video in videos:
                # Add randomized delay between oEmbed requests to be polite
                delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
                time.sleep(delay)
                
                # Enrich with oEmbed data
                oembed_data = OEmbedProvider.get_metadata(video["video_url"])
                if oembed_data:
                    video["title"] = oembed_data.get("title", video.get("title", ""))
                    video["thumbnail_url"] = oembed_data.get("thumbnail_url", "")
                    video["embed_html"] = oembed_data.get("embed_html", "")
                    
                    # Update creator name if we get it better from oEmbed
                    if "author_name" in oembed_data and oembed_data["author_name"]:
                         video["creator_name"] = oembed_data["author_name"]
                
                # Ensure approval_status is NOT overwritten if the video already exists
                # db.upsert_community_video handles this safely
                db.upsert_community_video(video)
                stats["videos_new"] += 1
                
        stats["status"] = "success"
        
    except Exception as e:
        logger.exception("Error in Stream B")
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
        logger.info(f"Stream B finished in {duration:.2f}s with status {stats['status']}")
        
    return stats

if __name__ == "__main__":
    run_stream_b()
