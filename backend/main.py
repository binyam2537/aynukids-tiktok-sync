import logging
import sys

# Validate config before anything else
import config
config.validate_config()

from scraper_channel import run_stream_a
from scraper_sounds import run_stream_b

logger = logging.getLogger("aynukids.main")

def main():
    logger.info("Starting AynuKids content pipeline")
    
    # Run Stream A (fetch channel videos and discover sound IDs)
    logger.info("=== Phase 1: Stream A ===")
    stats_a = run_stream_a()
    if stats_a["status"] != "success":
        logger.error(f"Stream A failed: {stats_a.get('error_message')}")
    
    # Run Stream B (fetch community videos using our sounds)
    logger.info("=== Phase 2: Stream B ===")
    stats_b = run_stream_b()
    if stats_b["status"] != "success":
        logger.error(f"Stream B failed: {stats_b.get('error_message')}")
        
    logger.info("Pipeline finished.")
    
    # Exit with error code if either stream failed
    if stats_a["status"] != "success" or stats_b["status"] != "success":
        sys.exit(1)

if __name__ == "__main__":
    main()
