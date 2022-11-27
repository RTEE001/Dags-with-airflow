import requests
from airflow.models import Variable
import json
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

TOKEN = Variable.get("TOKEN")
USERNAME = Variable.get("USERNAME")
GITHUB_API_LINK = "https://api.github.com/user/repos?per_page=100"


def read_url(url):
    url_response = requests.get(url, auth=(USERNAME, TOKEN))
    response = url_response.json()
    return response


def extract_prs_from_db(column_name):
    request = f"SELECT {column_name} FROM pr"
    pg_hook = PostgresHook(postgres_conn_id="postgres_db", schema="airflow")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    result = cursor.fetchall()
    return result


def create_and_populate_table_pr(html_url, api_url):
    return f"""
            CREATE TABLE IF NOT EXISTS pr(
                browser_url VARCHAR NOT NULL,
                api_url VARCHAR NOT NULL,
                reviews_url VARCHAR NOT NULL);
            INSERT INTO pr(browser_url, api_url, reviews_url)
            VALUES ('{html_url}', '{api_url}', '{api_url}/reviews')
        """


def create_and_populate_table_timestamps(html_url, timestamps):
    return f"""
            CREATE TABLE IF NOT EXISTS timestamps(      
                html_url VARCHAR NOT NULL,
                timestamp VARCHAR NOT NULL);
            INSERT INTO timestamps(html_url, timestamp)
            VALUES ('{html_url}', '{timestamps}')
        """


def timestamps(html_url, time):
    create_table_timestamps = PostgresOperator(
        task_id="create_table_timestamps",
        postgres_conn_id="postgres_db",
        sql=create_and_populate_table_timestamps(html_url, time),
    )
    create_table_timestamps.execute(dict())


def top_5_prs():
    request = f"""select distinct html_url from timestamps
                where timestamp 
                in (select max(timestamp)
                from timestamps group by  html_url)
                LIMIT 5;"""

    pg_hook = PostgresHook(postgres_conn_id="postgres_db", schema="airflow")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    result = cursor.fetchall()
    return result
