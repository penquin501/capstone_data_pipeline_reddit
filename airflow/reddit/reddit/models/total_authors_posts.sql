{{ config(materialized='table') }}
WITH post_data AS (
    SELECT
        author,
        COUNT(*) AS posts_count
    FROM {{ source('reddit_eng_posts', 'reddit_posts') }}
    GROUP BY author
)

SELECT
    COUNT(DISTINCT author) AS total_authors,
    SUM(posts_count) AS total_posts
FROM post_data