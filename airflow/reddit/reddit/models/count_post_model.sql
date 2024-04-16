{{ config(materialized='table') }}
select count(*)
from reddit_posts