from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TOKEN")
OWNER = os.getenv("OWNER")


def get_all_repos():
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
                repos_with_open_prs_details.append(each_object_['url'])

    return repos_with_open_prs_details

def get_timestamps():
    open_with_no_reviews =[]
    open_prs_with_reviews = []
    for each_pr in get_all_repos():
        comments_url = f"{each_pr}/reviews"
        url_response = requests.get(comments_url, auth=(OWNER, TOKEN))
        comments = url_response.json()
        if len(comments)==0:
            url = each_pr
            url_response = requests.get(comments_url, auth=(OWNER, TOKEN))
            comments = url_response.json()
            open_with_no_reviews.append(
                comments
            )
            continue
        else:
            open_prs_with_reviews.append({
                'submitted_at': comments["submitted_at"]
            })
    return open_with_no_reviews

print(get_timestamps())
