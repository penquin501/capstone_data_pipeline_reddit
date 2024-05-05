import pandas as pd
import matplotlib.pyplot as plt
import os
import streamlit as st
import psycopg2

from psycopg2.extras import RealDictCursor
from matplotlib.ticker import MaxNLocator
from jinja2 import Environment, FileSystemLoader

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from airflow.utils import timezone

def _get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",       # Your database host, e.g., "localhost" or an IP address
            dbname="postgres",   # Your database name
            user="postgres",   # Your database username
            password="postgres",  # Your database password
            port="5432"             # The port PostgreSQL is running on, typically 5432
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def _fetch_data(sql_query):
    conn = _get_db_connection()
    if conn:
        try:
            return pd.read_sql(sql_query, conn)
        finally:
            conn.close()
    else:
        return pd.DataFrame() 
    
def _get_average_scores():
    sql = "SELECT average_score FROM dbt_nattharee.average_score"
    data = _fetch_data(sql)
    return data

def _get_total_number_authors_and_posts():
    sql = "SELECT total_authors, total_posts FROM dbt_nattharee.total_authors_posts"
    data = _fetch_data(sql)
    return data

def _get_posts_per_day():
    sql = "SELECT post_date, posts_count FROM dbt_nattharee.posts_per_day"
    data = _fetch_data(sql)
    return data

def _get_avg_comments_per_day():
    sql = "SELECT comment_date, avg_comments FROM dbt_nattharee.avg_comments_per_day"
    data = _fetch_data(sql)
    return data

def _get_interesting_trend_topic():
    sql = "SELECT title, total_score, total_comments FROM dbt_nattharee.trending_topics"
    data = _fetch_data(sql)
    if not data.empty:
        # Set the index to start from 1 instead of 0
        data.index = data.index + 1
    return data

def plot_posts_per_day():
    data = _get_posts_per_day()
    if not data.empty:
        plt.figure(figsize=(10, 5))
        plt.bar(data['post_date'], data['posts_count'], color='#FF9130')
        plt.xlabel('Date')
        plt.ylabel('Number of Posts')
        plt.title('Posts per Day')
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt.gcf()  # Return the plot object without closing
    else:
        print("No data to display")
        return None
    
def plot_avg_comments_per_day():
    data = _get_avg_comments_per_day()
    if not data.empty:
        plt.figure(figsize=(10, 6))
        plt.hist(data['avg_comments'], bins=20, color='#FF5B22', edgecolor='black')
        plt.xlabel('Average Comments', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Histogram of Average Comments per Day', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        return plt.gcf()
    else:
        print("No data to display")
        return None

def main():
    total_authors_and_posts = _get_total_number_authors_and_posts()
    average_scores = _get_average_scores()
    trending_data = _get_interesting_trend_topic()

    st.title('Data Dashboard')
    st.write("### What are the total number of authors and posts in this subreddit?")

    col1, col2 = st.columns(2)
    
    if not total_authors_and_posts.empty:
        col1.markdown(f"<h4 style='color: #A9A9A9;'>The number of Authors: <strong style='color: #FF9130;'>{total_authors_and_posts['total_authors'].iloc[0]}</strong></h4>", 
                      unsafe_allow_html=True)
        col2.markdown(f"<h4 style='color: #A9A9A9;'>The number of Posts: <strong style='color: #FF9130;'>{total_authors_and_posts['total_posts'].iloc[0]}</strong></h4>", 
                      unsafe_allow_html=True)
    else:
        col1.markdown(f"<h4 style='color: #A9A9A9;'> No data available for Total Authors and Posts</h4>")

    st.write("### What is the average score?")
    col1, col2 = st.columns(2)
    if not average_scores.empty:
        col1.markdown(f"<h4 style='color: #A9A9A9;'>Average Score: <strong style='color: #FF9130;'>{average_scores['average_score'].iloc[0]}</strong></h4>", 
                      unsafe_allow_html=True)
    else:
        col1.markdown(f"<h4 style='color: #A9A9A9;'> Average Score: Data not available</h4>")

    st.write("### How many posts are published per day?")
    
    fig = plot_posts_per_day()
    if fig is not None:
        st.pyplot(fig)
        plt.close(fig)  # Close the plot after rendering in Streamlit
    else:
        st.write("No data available to plot.")

    st.write("### What is the average number of comments per day?")
    fig_comments = plot_avg_comments_per_day()
    if fig_comments is not None:
        st.pyplot(fig_comments)
        plt.close(fig_comments)  # Ensure that the plot is closed after rendering
    else:
        st.write("No data available to plot for Average Comments per Day.")

    st.write("### Is there any interesting trend at this moment?")
    st.write("### Trending Topics")
    if not trending_data.empty:
        st.dataframe(trending_data)  # This line will display the data in an interactive table
    else:
        st.write("No trending topics data available.")


if __name__ == "__main__":
    main()

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'email': ['66130047@dpu.ac.th'],
    'retries': 1
}

# Define the DAG
with DAG(
    "dbt_visualization",
    default_args=default_args,
    description="DAG for fetching Reddit data, running dbt, and visualizing outputs",
    schedule_interval="@daily",
    start_date=timezone.datetime(2024, 4, 14),
    catchup=False
):
    start = EmptyOperator(task_id="start")

    get_db_connection = PythonOperator(
        task_id="get_db_connection",
        python_callable=_get_db_connection,
    )
    
    end = EmptyOperator(task_id="end")

    start >> get_db_connection >> end
