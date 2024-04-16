{{ config(materialized='table') }}
WITH post_data AS (
    SELECT
        author_fullname,
        COUNT(*) AS posts_count
    FROM {{ source('reddit_eng_posts', 'reddit_posts') }}
    GROUP BY author_fullname
)

SELECT
    COUNT(DISTINCT author_fullname) AS total_authors,
    SUM(posts_count) AS total_posts
FROM post_data