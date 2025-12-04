-- Migration: Restructure seasonal_stories table
-- Date: 2025-12-03
-- Purpose: Remove store_type, add featured_menu_name, simplify structure

-- Step 1: Add new columns
ALTER TABLE seasonal_stories
ADD COLUMN featured_menu_name VARCHAR(100) AFTER store_name,
ADD COLUMN is_special_day TINYINT(1) DEFAULT 0 AFTER time_period,
ADD COLUMN is_weekend TINYINT(1) DEFAULT 0 AFTER is_special_day,
ADD COLUMN trend_keywords JSON AFTER is_weekend;

-- Step 2: Drop old columns
ALTER TABLE seasonal_stories
DROP COLUMN store_type,
DROP COLUMN menu_items,
DROP COLUMN google_trends,
DROP COLUMN instagram_trends,
DROP COLUMN selected_trends;

-- Step 3: Modify store_id to NOT NULL (after cleanup)
-- Note: First clean up data where store_id is NULL or 0
DELETE FROM seasonal_stories WHERE store_id IS NULL OR store_id = 0 OR store_id = 1;

-- Step 4: Add index for performance
CREATE INDEX idx_store_conditions ON seasonal_stories(
    store_id,
    weather_condition,
    temperature,
    is_special_day,
    is_weekend
);

-- Step 5: Verify changes
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT store_id) as unique_stores
FROM seasonal_stories;
