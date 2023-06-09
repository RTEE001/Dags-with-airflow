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


def create_table_pr():
    create_table_pr = PostgresOperator(
        task_id="create_table_pr",
        postgres_conn_id="postgres_db",
        sql=f"""
            CREATE TABLE IF NOT EXISTS pr(
                browser_url VARCHAR NOT NULL,
                api_url VARCHAR NOT NULL,
                reviews_url VARCHAR NOT NULL);
            """,
    )
    create_table_pr.execute(dict())


def populate_table_pr(html_url, api_url):
    populate_table_pr = PostgresOperator(
        task_id="populate_table_pr",
        postgres_conn_id="postgres_db",
        sql=f"""
            INSERT INTO pr(browser_url, api_url, reviews_url)
            VALUES ('{html_url}', '{api_url}', '{api_url}/reviews')
        """,
    )
    populate_table_pr.execute(dict())


def create_table_timestamps():
    create_table_timestamps = PostgresOperator(
        task_id="create_table_timestamps",
        postgres_conn_id="postgres_db",
        sql=f"""
            CREATE TABLE IF NOT EXISTS timestamps(      
                html_url VARCHAR NOT NULL,
                timestamp VARCHAR NOT NULL);
            """,
    )
    create_table_timestamps.execute(dict())


def populate_table_timestamps(html_url, timestamps):
    populate_table_timestamps = PostgresOperator(
        task_id="populate_table_timestamps",
        postgres_conn_id="postgres_db",
        sql=f"""
            INSERT INTO timestamps(html_url, timestamp)
            VALUES ('{html_url}', '{timestamps}')
        """,
    )
    populate_table_timestamps.execute(dict())


def get_top_5_prs():
    request = f"""
    drop table if exists temp_table;
    select distinct html_url, timestamp into table temp_table from timestamps
    where timestamp in 
    (select max(timestamp) from timestamps group by  html_url)
    order by timestamp asc
    LIMIT 5;
    select html_url from temp_table;"""

    pg_hook = PostgresHook(postgres_conn_id="postgres_db", schema="airflow")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    result = cursor.fetchall()
    return result
