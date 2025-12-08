-- Supabase Database Schema for Portfolio Analytics
-- Run this in Supabase SQL Editor: https://app.supabase.com/project/_/sql

-- ============================================================================
-- VISITS TABLE
-- Tracks page views with device, location, and engagement metrics
-- ============================================================================

CREATE TABLE IF NOT EXISTS visits (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session tracking
    session_id TEXT NOT NULL,

    -- Visitor information (privacy-conscious)
    ip_hash TEXT,  -- Hashed IP for privacy compliance
    country TEXT,
    city TEXT,

    -- Device & Browser information
    user_agent TEXT,
    device_type TEXT CHECK (device_type IN ('mobile', 'tablet', 'desktop', 'bot')),
    browser TEXT,
    browser_version TEXT,
    os TEXT,
    os_version TEXT,
    screen_width INT,
    screen_height INT,

    -- Page tracking
    page_url TEXT NOT NULL,
    page_title TEXT,
    referrer TEXT,

    -- Engagement metrics
    time_on_page INT,  -- seconds
    scroll_depth INT CHECK (scroll_depth >= 0 AND scroll_depth <= 100),  -- percentage

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_visits_session_id ON visits(session_id);
CREATE INDEX IF NOT EXISTS idx_visits_created_at ON visits(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_visits_page_url ON visits(page_url);
CREATE INDEX IF NOT EXISTS idx_visits_device_type ON visits(device_type);
CREATE INDEX IF NOT EXISTS idx_visits_country ON visits(country);

-- RLS (Row Level Security) - Enable if needed
-- ALTER TABLE visits ENABLE ROW LEVEL SECURITY;

-- Policy to allow inserts from API (adjust based on your security needs)
-- CREATE POLICY "Allow public inserts" ON visits FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow authenticated reads" ON visits FOR SELECT USING (auth.role() = 'authenticated');


-- ============================================================================
-- CONTACT_MESSAGES TABLE
-- Stores contact form submissions
-- ============================================================================

CREATE TABLE IF NOT EXISTS contact_messages (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Contact information
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL CHECK (char_length(message) >= 10 AND char_length(message) <= 5000),

    -- Metadata
    ip_address TEXT,  -- For spam prevention
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Status tracking (optional)
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'read', 'replied', 'archived'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contact_messages_created_at ON contact_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contact_messages_email ON contact_messages(email);
CREATE INDEX IF NOT EXISTS idx_contact_messages_status ON contact_messages(status);

-- RLS
-- ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow public inserts" ON contact_messages FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow admin reads" ON contact_messages FOR SELECT USING (auth.role() = 'authenticated');


-- ============================================================================
-- EVENTS TABLE
-- Tracks custom events (clicks, downloads, form submissions, etc.)
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event information
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'click', 'download', 'form_submit', etc.
    event_data JSONB DEFAULT '{}',  -- Flexible JSON storage for event-specific data

    -- Context
    page_url TEXT,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_data ON events USING GIN(event_data);  -- For JSONB queries

-- RLS
-- ALTER TABLE events ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow public inserts" ON events FOR INSERT WITH CHECK (true);


-- ============================================================================
-- HELPER VIEWS (Optional but useful)
-- ============================================================================

-- Daily visits summary
CREATE OR REPLACE VIEW daily_visits AS
SELECT
    DATE(created_at) as visit_date,
    COUNT(*) as total_visits,
    COUNT(DISTINCT session_id) as unique_visitors,
    COUNT(*) FILTER (WHERE device_type = 'mobile') as mobile_visits,
    COUNT(*) FILTER (WHERE device_type = 'desktop') as desktop_visits,
    COUNT(*) FILTER (WHERE device_type = 'tablet') as tablet_visits
FROM visits
WHERE device_type != 'bot'  -- Exclude bots
GROUP BY DATE(created_at)
ORDER BY visit_date DESC;

-- Popular pages
CREATE OR REPLACE VIEW popular_pages AS
SELECT
    page_url,
    COUNT(*) as visit_count,
    COUNT(DISTINCT session_id) as unique_visitors,
    AVG(time_on_page) as avg_time_on_page,
    AVG(scroll_depth) as avg_scroll_depth
FROM visits
WHERE device_type != 'bot'
GROUP BY page_url
ORDER BY visit_count DESC;

-- Traffic sources
CREATE OR REPLACE VIEW traffic_sources AS
SELECT
    CASE
        WHEN referrer IS NULL OR referrer = '' THEN 'Direct'
        WHEN referrer LIKE '%linkedin.com%' THEN 'LinkedIn'
        WHEN referrer LIKE '%github.com%' THEN 'GitHub'
        WHEN referrer LIKE '%google.com%' THEN 'Google'
        ELSE 'Other'
    END as source,
    COUNT(*) as visit_count,
    COUNT(DISTINCT session_id) as unique_visitors
FROM visits
WHERE device_type != 'bot'
GROUP BY source
ORDER BY visit_count DESC;


-- ============================================================================
-- CLEANUP FUNCTION (Optional - for GDPR compliance)
-- Automatically delete old data after 90 days
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_old_analytics()
RETURNS void AS $$
BEGIN
    DELETE FROM visits WHERE created_at < NOW() - INTERVAL '90 days';
    DELETE FROM events WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Uncomment to create a scheduled job (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-analytics', '0 2 * * *', 'SELECT cleanup_old_analytics()');


-- ============================================================================
-- GRANT PERMISSIONS
-- Grant necessary permissions for API access
-- ============================================================================

-- If using service role key, these may not be needed
-- GRANT INSERT ON visits TO anon, authenticated;
-- GRANT INSERT ON contact_messages TO anon, authenticated;
-- GRANT INSERT ON events TO anon, authenticated;
-- GRANT SELECT ON visits TO authenticated;
-- GRANT SELECT ON contact_messages TO authenticated;
-- GRANT SELECT ON events TO authenticated;


-- ============================================================================
-- VERIFICATION
-- Run these queries to verify the schema was created successfully
-- ============================================================================

-- Check tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('visits', 'contact_messages', 'events');

-- Check indexes
SELECT indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('visits', 'contact_messages', 'events');

-- Test insert (remove after verification)
-- INSERT INTO visits (session_id, page_url, device_type, browser)
-- VALUES ('test-session-123', '/test', 'desktop', 'Chrome');

-- Verify insert
-- SELECT * FROM visits WHERE session_id = 'test-session-123';

-- Clean up test data
-- DELETE FROM visits WHERE session_id = 'test-session-123';
