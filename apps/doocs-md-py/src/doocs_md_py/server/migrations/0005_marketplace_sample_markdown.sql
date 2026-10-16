-- upstream: apps/api/migrations/0005_marketplace_sample_markdown.sql（原样移植）
-- Optional sample Markdown for theme preview (NULL = use client system default)
ALTER TABLE marketplace_items ADD COLUMN sample_markdown TEXT;
