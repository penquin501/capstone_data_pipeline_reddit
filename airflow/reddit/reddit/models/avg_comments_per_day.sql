
SELECT 
    DATE(created_utc) AS comment_date,
    AVG(num_comments) AS avg_comments
    
FROM {{ source('reddit_eng_posts', 'reddit_posts') }}
GROUP BY DATE(created_utc)