-- ================================================================================
-- AynuKids Database Functions
-- Run this in the Supabase SQL Editor AFTER schema.sql
-- ================================================================================

-- A function to fetch random videos for the infinite scroll feed
-- Call via POST /rest/v1/rpc/get_random_feed
CREATE OR REPLACE FUNCTION get_random_feed(limit_count integer DEFAULT 10)
RETURNS TABLE (
    id TEXT,
    video_url TEXT,
    title TEXT,
    thumbnail_url TEXT,
    embed_html TEXT,
    author_name TEXT,
    type TEXT -- 'brand' or 'community'
) LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH combined AS (
        SELECT 
            v.id, 
            v.video_url, 
            v.title, 
            v.thumbnail_url, 
            v.embed_html, 
            v.author_name,
            'brand' AS type
        FROM videos v
        WHERE v.is_active = true
        
        UNION ALL
        
        SELECT 
            c.id, 
            c.video_url, 
            c.title, 
            c.thumbnail_url, 
            c.embed_html, 
            c.creator_name AS author_name,
            'community' AS type
        FROM community_videos c
        WHERE c.approval_status = 'approved'
    )
    SELECT * FROM combined
    ORDER BY random()
    LIMIT limit_count;
END;
$$;
