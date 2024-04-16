{{ config(materialized='table') }}
SELECT
    DATE(created_utc) AS post_date,
    COUNT(*) AS posts_count
FROM {{ source('reddit_eng_posts', 'reddit_posts') }}
GROUP BY DATE(created_utc)