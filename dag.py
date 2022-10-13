from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG("my_dag", # Dag id
start_date=datetime(2020, 1 ,1), # start date, the 1st of January 2021 
schedule_interval='@daily',  # Cron expression, here it is a preset of Airflow, @daily means once every day.
catchup=False  # Catchup 
) as dag: