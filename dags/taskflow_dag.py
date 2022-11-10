from airflow.models import Variable
from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator

GITHUB_API_LINK = "https://api.github.com/user/repos?per_page=100"

with DAG(
    'pr_filter',
    
    default_args = {
        "owner": "airflow", 
        "start_date": datetime(2022,10,1)
    }, 
    description = "A DAG to get top 5 open PRs",
    schedule = timedelta(minutes = 5),
    catchup = False,
    tags = ["pr"]
)