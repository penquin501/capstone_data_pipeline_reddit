{{ config(materialized='table') }}
SELECT
    title,
    SUM(score) AS total_score,
    SUM(num_comments) AS total_comments,
    DATE(created_utc) AS post_date
    
FROM {{ source('reddit_eng_posts', 'reddit_posts') }}
GROUP BY title, DATE(created_utc)
ORDER BY total_score DESC, total_comments DESC
LIMIT 10