-- ================================================================================
-- AynuKids Row Level Security (RLS) Policies
-- Run this in the Supabase SQL Editor AFTER schema.sql
-- ================================================================================

-- Enable RLS on all tables
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE sounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_log ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------------------
-- 1. Public Read Access (for the Flutter app)
-- --------------------------------------------------------------------------------

-- Anyone can view active brand videos
CREATE POLICY "Public can view active brand videos"
ON videos FOR SELECT
USING (is_active = true);

-- Anyone can view approved community videos
CREATE POLICY "Public can view approved community videos"
ON community_videos FOR SELECT
USING (approval_status = 'approved');

-- Anyone can view active sounds
CREATE POLICY "Public can view active sounds"
ON sounds FOR SELECT
USING (is_active = true);

-- --------------------------------------------------------------------------------
-- 2. Authenticated Admin Access (for Supabase Studio / Admin Dashboard)
-- --------------------------------------------------------------------------------
-- Note: Service Role (used by Python scripts) automatically bypasses RLS.
-- These policies are for users logging into a potential admin dashboard.

-- Authenticated admins can manage community videos (to approve/reject)
CREATE POLICY "Admins can update community videos"
ON community_videos FOR UPDATE
TO authenticated
USING (true);

CREATE POLICY "Admins can view all community videos"
ON community_videos FOR SELECT
TO authenticated
USING (true);

-- Admins can view logs
CREATE POLICY "Admins can view logs"
ON sync_log FOR SELECT
TO authenticated
USING (true);

-- Admins can view/manage sounds
CREATE POLICY "Admins can manage sounds"
ON sounds FOR ALL
TO authenticated
USING (true);

-- Admins can view/manage brand videos
CREATE POLICY "Admins can manage brand videos"
ON videos FOR ALL
TO authenticated
USING (true);
