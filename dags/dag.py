from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
# from dotenv import load_dotenv
import requests

# load_dotenv()
# TOKEN = os.getenv("TOKEN")
# OWNER = os.getenv("OWNER")


def  get_all_open_prs():

    accessible_repos_url = f"https://api.github.com/user/repos?per_page=100"
    accessible_repos_url_response = requests.get(
        accessible_repos_url, auth=(OWNER, TOKEN)
    )
    accessible_repos = accessible_repos_url_response.json()
    repos_with_open_prs_details = []
    for each_object in accessible_repos:
        url = f"{each_object['url']}/pulls"
        url_response = requests.get(url, auth=(OWNER, TOKEN))
        repos_with_open_prs = url_response.json()

        for each_object_ in repos_with_open_prs:
            if len(each_object_) != 0:
                repos_with_open_prs_details.append({each_object_['html_url']: each_object_["url"] })

    return repos_with_open_prs_details

def get_timestamps():
    timestamps = []
    for i in get_all_open_prs():
        for key, val in i.items():
            print(val)
            comments_url = f"{val}/reviews"
            url_response = requests.get(comments_url, auth=(OWNER, TOKEN))
            comments = url_response.json()
            for k in comments:
                timestamps.append({key:k["submitted_at"]})

    return timestamps
 
default_args = {
    'owner' :'airflow',
    'start_date': datetime(2022, 10, 1),
}

pr_dag = DAG(
    'pr_filter',
    default_args = default_args, 
    description =  'notifies the user which pull requests need attention',
    schedule = timedelta(minutes = 5), 
    catchup = False
)

task1 = PythonOperator(
    task_id = 'get_all_open_prs',
    python_callable = get_all_open_prs,
    dag = pr_dag, 
)


task2 = PythonOperator(
    task_id = 'get_timestamps',
    python_callable = get_timestamps,
    dag = pr_dag, 
)

# task3 = PythonOperator(
#     task_id = 'send_email',
#     python_callable = send_email,
#     dag = pr_dag, 
# )

task1 >> task2 




# def get_timestamps():
#     open_with_no_reviews =[]
#     open_prs_with_reviews = []
#     for each_pr in get_all_repos():
#         comments_url = f"{each_pr}/reviews"
#         url_response = requests.get(comments_url, auth=(OWNER, TOKEN))
#         comments = url_response.json()
#         if len(comments)==0:
#             url = each_pr
#             url_response = requests.get(comments_url, auth=(OWNER, TOKEN))
#             comments = url_response.json()
#             open_with_no_reviews.append(
#                 comments
#             )
#             continue
#         else:
#             open_prs_with_reviews.append({
#                 'submitted_at': comments["submitted_at"]
#             })
#     return open_with_no_reviews

# print(get_timestamps())