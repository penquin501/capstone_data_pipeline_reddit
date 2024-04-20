import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MaxNLocator
from jinja2 import Environment, FileSystemLoader

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from airflow.utils import timezone
from airflow.models import Variable

def _mockup_dashboard(**kwargs):
    # Define the path to the templates directory
    template_loader = FileSystemLoader(searchpath="/opt/airflow/dags/templates")
    env = Environment(loader=template_loader)

    # Load the template from the templates directory
    template = env.get_template('dashboard_template.html')

    # Mock data for the dashboard
    data = {
        'total_posts': 150,
        'average_score': get_average_score().average_score.item(),
        'total_comments': 200,
        'trending_topics': ['Data Engineering', 'Machine Learning', 'Data Visualization'],
    }

    # Render the template with the mock data
    rendered_html = template.render(data=data)

    # Write the rendered HTML to a file
    output_dir = '/opt/airflow/dags/output'
    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, f"dashboard.html")

    with open(output_file_path, 'w') as file:
        file.write(rendered_html)

    print(f'Dashboard has been created: {output_file_path}')
    
def get_average_score():
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    sql = """
        select average_score from dbt_nattharee.average_score
    """
    cursor.execute(sql)
    connection.commit()
    
    df = pd.read_sql_query(sql, connection)
    
    connection.commit()
    cursor.close()
    connection.close()

    return df



def _generate_visualizations(**context):
    pg_hook = PostgresHook(
        postgres_conn_id="my_postgres_conn",
        schema="postgres"
    )
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    sql = """
        select * from dbt_nattharee.posts_per_day
    """
    cursor.execute(sql)
    connection.commit()
    
    df = pd.read_sql_query(sql, connection)

    if not df.empty:
        # Plotting the data
        fig, axs = plt.subplots(3, 2, figsize=(15, 15))  # Adjust the layout as needed
        fig.suptitle('DBT Models Dashboard', fontsize=20)

        


        # Tight layout with top title space
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_dir = '/opt/airflow/dags/output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = context['execution_date'].strftime('%Y%m%d%H%M%S')
        filename = f"{output_dir}/trending_topics_{timestamp}.png"

        plt.savefig(filename, bbox_inches='tight')
        plt.close()
    else:
        print("No data available to plot.")

    connection.commit()
    cursor.close()
    connection.close()

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
    
    # generate_visualizations = PythonOperator(
    #     task_id="generate_visualizations",
    #     python_callable=_generate_visualizations,
    # )

    mockup_dashboard = PythonOperator(
        task_id="mockup_dashboard",
        python_callable=_mockup_dashboard,
    )
    
    end = EmptyOperator(task_id="end")

    start >> mockup_dashboard >> end
