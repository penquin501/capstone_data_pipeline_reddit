import json
import requests
import praw

from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import timezone

import great_expectations as gx
import pandas as pd
from great_expectations.dataset import PandasDataset
from datetime import datetime

# Define your credentials
CLIENT_ID = Variable.get("CLIENT_ID")
CLIENT_SECRET = Variable.get("CLIENT_SECRET")
USER_AGENT = Variable.get("USER_AGENT")

def _get_reddit_data(**context):
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        check_for_async=False  # Important for running with Airflow
    )

    subreddit = reddit.subreddit('dataengineering')
    top_posts = subreddit.top(limit=None)

    _save_to_database(top_posts)


def _create_reddit_table(**context):
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    sql = """
        CREATE TABLE IF NOT EXISTS reddit_posts (
            post_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ups INTEGER NOT NULL,
            author_fullname TEXT,
            subreddit TEXT,
            selftext TEXT,
            url TEXT,
            num_comments INTEGER,
            created_utc TIMESTAMP
        )
    """
    cursor.execute(sql)
    connection.commit()

def _save_to_database(data):
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn", 
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO reddit_posts (post_id, title, ups, author_fullname, subreddit, selftext, url, num_comments, created_utc)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (post_id) DO NOTHING;
    """
    for post in data:
        print(f"title: {post.title}")
        data_tuple = (
            post.id, 
            post.title, 
            post.ups, 
            post.name,
            post.subreddit.display_name, 
            post.selftext, 
            post.url,
            post.num_comments, 
            datetime.fromtimestamp(post.created_utc)
        )
        cursor.execute(insert_query, data_tuple)

    connection.commit()
    cursor.close()
    connection.close()


default_args = {
    "email": ["66130047@dpu.ac.th"],
    "retries": 1,
    # "retry_delay": timedelta(minutes=5),
}

with DAG(
    "reddit_api_dag",
    default_args=default_args,
    description="DAG for fetching data from Reddit API",
    schedule_interval="@daily",
    start_date=timezone.datetime(2024, 4, 14),
    catchup=False,
):
    
    start = EmptyOperator(task_id="start")
    
    create_reddit_table = PythonOperator(
        task_id="create_reddit_table",
        python_callable=_create_reddit_table,
    )

    get_reddit_data = PythonOperator(
        task_id="get_reddit_data",
        python_callable=_get_reddit_data,  # Ensure this function is defined in your DAG's context
    )
    
    end = EmptyOperator(task_id="end")

    start >> create_reddit_table >> get_reddit_data >> end