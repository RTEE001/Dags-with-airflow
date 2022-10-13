# We'll start by importing the DAG object
from airflow import DAG
# We need to import the operators used in our tasks
from airflow.operators.bash_operator import BashOperator
# We then import the days_ago function
from airflow.utils.dates import days_ago