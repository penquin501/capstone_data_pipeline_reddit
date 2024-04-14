import json
import requests
import praw

from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils import timezone

# import great_expectations as gx
# import pandas as pd
# from great_expectations.dataset import PandasDataset

def _get_reddit_data(**context):
    reddit = praw.Reddit(
        client_id='1G__EXR9bO3UoYdaYaIJ2w',
        client_secret='oyzHIfMJi4I8YvgxvF6M16UUHNXrrw',
        user_agent='python:MyRedditDataApp:1.0 (by /u/Rich_Type_2395)'
    )

    subreddit = reddit.subreddit('dataengineering')
    for post in subreddit.new(limit=10):
        print(f"post: {post}")
        print("------------------------------")




# default_args = {
#     "email": ["66130047@dpu.ac.th"],
#     # "retries": 1,
# }

# with DAG(
#     "reddit_api_dag",
#     default_args=default_args,
#     schedule="@Daily",
#     start_date=timezone.datetime(2024, 4, 1),
#     catchup=False,
# ):
#     start = EmptyOperator(task_id="start")

#     get_reddit_data = PythonOperator(
#         task_id="get_reddit_data",
#         python_callable=_get_reddit_data,
#     )

#     end = EmptyOperator(task_id="end")

#     start >> get_reddit_data >> end