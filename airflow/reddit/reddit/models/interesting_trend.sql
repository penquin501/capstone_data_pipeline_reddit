
{{ config(materialized='table') }}
SELECT 
    title, created_utc, score, num_comments

FROM 
    {{ source('reddit_eng_posts', 'reddit_posts') }}

WHERE 
    created_utc >= current_date - interval '30 days'
    
ORDER BY created_utc DESC