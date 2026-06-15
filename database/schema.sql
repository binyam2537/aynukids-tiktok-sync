-- ================================================================================
-- AynuKids Supabase Schema
-- Run this in the Supabase SQL Editor
-- ================================================================================

-- 1. Track our channel's original sounds
CREATE TABLE IF NOT EXISTS sounds (
    id TEXT PRIMARY KEY,                       -- TikTok sound ID (stored as text to prevent JS BigInt issues)
    title TEXT,                                -- Sound name
    author_name TEXT DEFAULT 'AynuKids',
    origin_video_id TEXT,                      -- Video that created this sound
    music_url TEXT,                            -- TikTok music page URL
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE             -- Whether to track reposts
);

-- 2. Our brand's official videos (Stream A)
CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,                       -- TikTok video ID
    video_url TEXT NOT NULL,                   -- Full TikTok URL
    title TEXT,                                -- Caption/description
    thumbnail_url TEXT,                        -- Thumbnail from oEmbed
    embed_html TEXT,                           -- oEmbed embed code
    sound_id TEXT REFERENCES sounds(id),
    author_name TEXT DEFAULT 'AynuKids አይኑ ኪድስ',
    created_at TIMESTAMPTZ,                    -- When video was posted
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE             -- Hide without deleting
);

-- 3. Fan/community videos that reuse our sounds (Stream B)
CREATE TABLE IF NOT EXISTS community_videos (
    id TEXT PRIMARY KEY,                       -- TikTok video ID
    video_url TEXT NOT NULL,
    title TEXT,
    thumbnail_url TEXT,
    embed_html TEXT,
    sound_id TEXT REFERENCES sounds(id),
    creator_handle TEXT NOT NULL,              -- Fan's @username
    creator_name TEXT,                         -- Fan's display name
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approval_status TEXT DEFAULT 'pending'     -- 'pending' | 'approved' | 'rejected'
        CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    reviewed_by TEXT,                          -- Admin who reviewed
    reviewed_at TIMESTAMPTZ
);

-- 4. Ingestion run log for monitoring
CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    run_at TIMESTAMPTZ DEFAULT NOW(),
    stream TEXT NOT NULL,                      -- 'channel' or 'sounds'
    status TEXT NOT NULL,                      -- 'success' | 'partial' | 'failed'
    videos_found INTEGER DEFAULT 0,
    videos_new INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL
);

-- 5. Indexes for API performance
CREATE INDEX IF NOT EXISTS idx_videos_active ON videos(is_active, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_approved ON community_videos(approval_status, discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_sound ON community_videos(sound_id);

-- Ensure updated_at triggers exist
CREATE OR REPLACE FUNCTION update_modified_column() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;   
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_videos_modtime ON videos;
CREATE TRIGGER update_videos_modtime 
    BEFORE UPDATE ON videos 
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

DROP TRIGGER IF EXISTS update_community_videos_modtime ON community_videos;
CREATE TRIGGER update_community_videos_modtime 
    BEFORE UPDATE ON community_videos 
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
