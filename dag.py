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
    accessible_repos_url = f" https://api.github.com/user/repos?per_page=100"
    accessible_repos_url_response = requests.get(accessible_repos_url, auth=(OWNER, TOKEN))
    accessible_repos = accessible_repos_url_response.json()
    repos_with_open_prs_details = []
    for each_object in accessible_repos:
        url = f"{each_object['url']}/pulls"
        url_response = requests.get(url, auth=(OWNER, TOKEN))
        repos_with_open_prs = url_response.json()
        
        for each_object in repos_with_open_prs:
            if len(each_object) !=0:
                repos_with_open_prs_details.append(
                    each_object
                )

    return repos_with_open_prs_details

print(get_all_repos())