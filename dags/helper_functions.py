import requests
from airflow.models import Variable
import json
from airflow.hooks.postgres_hook import PostgresHook

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


def create_and_populate_table(browser_url, api_url):
    return f"""
            CREATE TABLE IF NOT EXISTS pr(
                browser_url VARCHAR NOT NULL,
                api_url VARCHAR NOT NULL,
                reviews_url VARCHAR NOT NULL);
            INSERT INTO pr(browser_url, api_url, reviews_url)
            VALUES ('{browser_url}', '{api_url}', '{api_url}/reviews')
        """

def add_column_to_db(col_name):
    add_column_to_db = PostgresOperator(
        task_id="add_column",
        postgres_conn_id="postgres_db",
        sql=f"""
            ALTER TABLE pr
            ADD {col_name} VARCHAR; 
            """
    )
    add_column_to_db.execute(dict())

def add_items_to_db(col_name, item):
    add_items_to_db= PostgresOperator(
        task_id="add_item",
        postgres_conn_id="postgres_db",
        sql=f"""
            INSERT INTO pr({col_name})
            VALUES ('{item}')
            """
    )
    add_items_to_db.execute(dict())


def filter_timestamps_by_latest_time(pr_list):
    result_dict = {}
    for item in pr_list:
        key = list(item.keys())[0]
        if key in result_dict:
            if item[key] > result_dict[key][key]:
                result_dict.update({key: item})
        else:
            result_dict.update({key: item})
    result_list = [v for k, v in result_dict.items()]
    return result_list


def sort_timestamps(pr_list):
    values = []
    sorted_timestamps = []

    for each_dict in pr_list:
        values.append(list(each_dict.values())[0])

    values.sort(reverse=True)

    for each_dict in pr_list:
        insert_index = values.index(list(each_dict.values())[0])
        sorted_timestamps.insert(
            insert_index, {list(each_dict.keys())[0]: values[insert_index]}
        )
    return sorted_timestamps


def get_top_five_prs(pr_list):
    urgent_prs = []
    if len(pr_list) > 5:
        for i in range(5):
            urgent_prs.append(pr_list[i])
        return urgent_prs
    return pr_list
