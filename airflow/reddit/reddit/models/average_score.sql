{{ config(materialized='table') }}
SELECT
    AVG(score) AS average_score

FROM {{ source('reddit_eng_posts', 'reddit_posts') }}