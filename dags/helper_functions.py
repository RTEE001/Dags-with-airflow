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


def extract_from_db(table_name):
    request = f"SELECT * FROM {table_name}"
    pg_hook = PostgresHook(postgres_conn_id="postgres_db", schema="airflow")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute(request)
    result = cursor.fetchall()
    return result


def create_and_populate_table(table_name, value):
    return f"""
            CREATE TABLE IF NOT EXISTS {table_name}(
                name VARCHAR(10000)
            );
            INSERT INTO {table_name}(name)
            VALUES ('{value}')
        """


def get_timestamps(pr_list):
    timestamps = []
    pr_list = [item for t in pr_list for item in t]
    for i in pr_list:
        i = json.loads(i)
        for key, val in i.items():
            comments = read_url(f"{val}/reviews")
            if len(comments) == 0:
                url = read_url(val)
                if url["updated_at"] != None:
                    timestamps.append({url["html_url"]: url["updated_at"]})
                else:
                    timestamps.append({url["html_url"]: url["created_at"]})
            else:
                for k in comments:
                    timestamps.append({key: k["submitted_at"]})
    return timestamps


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
