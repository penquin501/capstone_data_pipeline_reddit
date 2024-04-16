from airflow.utils import timezone

from cosmos import DbtDag, ProjectConfig, ProfileConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


profile_config = ProfileConfig(
    profile_name="reddit",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="my_postgres_conn",
        profile_args={"schema": "dbt_nattharee"},
    ),
)

reddit_dbt_dag = DbtDag(
    dag_id="reddit_dbt_dag",
    schedule_interval="@daily",
    start_date=timezone.datetime(2024, 4, 1),
    catchup=False,
    project_config=ProjectConfig("/opt/airflow/dbt/reddit"),
    profile_config=profile_config
)
