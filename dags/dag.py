from airflow import DAG
from airflow.operators.python import PythonOperator
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
import requests

TOKEN = os.getenv("TOKEN")
OWNER = os.getenv("OWNER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL_ADDRESS = os.getenv("SENDER_EMAIL_ADDRESS")
RECEIPIENT_EMAIL_ADDRESS = os.getenv("RECEIPIENT_EMAIL_ADDRESS")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def read_url(url):
    url_response = requests.get(url, auth=(OWNER, TOKEN))
    response = url_response.json()
    return response

def get_all_open_prs():

    repos_with_open_prs_details = []
    all_pr_response = read_url("https://api.github.com/user/repos?per_page=100")
    for each_object in all_pr_response:
        repos_with_open_prs = read_url(f"{each_object['url']}/pulls")
        for each_object_ in repos_with_open_prs:
            if len(each_object_) != 0:
                repos_with_open_prs_details.append(
                    {each_object_["html_url"]: each_object_["url"]}
                )

    return repos_with_open_prs_details


def get_timestamps():
    timestamps = []
    for i in get_all_open_prs():
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

def filter_timestamps_by_latest_time():
    result_dict = {}
    for item in get_timestamps():
        key = list(item.keys())[0]
        if key in result_dict:
            if item[key] > result_dict[key][key]:
                result_dict.update({key: item})
        else:
            result_dict.update({key: item})
    result_list = [v for k, v in result_dict.items()]
    return result_list

def sort_timestamps():
    values = []
    sorted_timestamps = []

    for each_dict in filter_timestamps_by_latest_time():
        values.append(list(each_dict.values())[0])

    values.sort(reverse=True)

    for each_dict in filter_timestamps_by_latest_time():
        insert_index = values.index(list(each_dict.values())[0])
        sorted_timestamps.insert(insert_index, {
            list(each_dict.keys())[0] : values[insert_index]
        })
    return sorted_timestamps

def get_top_five_prs():
    urgent_prs = []
    if len(sort_timestamps()) >5:
        for i in range(5):
            urgent_prs.append(sort_timestamps()[i])
        return urgent_prs     
    return sort_timestamps()

def consolidate_pull_requests():
    links = []

    for each_dict in get_top_five_prs():
        links.append(list((each_dict.keys()))[0])
    return "\n\n".join(links)


def send_email():
    
    subject = "Urgent pull requests that need attention"
    body = consolidate_pull_requests()

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL_ADDRESS
    msg["To"] = RECEIPIENT_EMAIL_ADDRESS

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(SENDER_EMAIL_ADDRESS, SMTP_PASSWORD)
    smtp.sendmail(SENDER_EMAIL_ADDRESS, RECEIPIENT_EMAIL_ADDRESS, msg.as_string())
    smtp.quit()



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

get_open_prs = PythonOperator(
    task_id = 'get_all_open_prs',
    python_callable = get_all_open_prs,
    dag = pr_dag, 
)


get_latest_timestamps = PythonOperator(
    task_id = 'get_timestamps',
    python_callable = consolidate_pull_requests,
    dag = pr_dag, 
)

send_pr_email = PythonOperator( 
task_id='send_email', 
python_callable = send_email , 
dag=pr_dag)

get_open_prs >> get_latest_timestamps >> send_pr_email