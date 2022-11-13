from airflow.models import Variable
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import json
from airflow.providers.postgres.operators.postgres import PostgresOperator

GITHUB_API_LINK = "https://api.github.com/user/repos?per_page=100"

default_args = {
    'owner' :'airflow',
    'start_date': datetime(2022, 10, 1),
}

@dag(
    schedule = timedelta(minutes = 3),
    default_args = default_args,
    catchup=False,
    description =  'notifies the user which pull requests need attention',
    tags=['pr'],
)

def pr_filter():
    @task
    def get_all_open_prs():
        from helper_functions import read_url
        repos_with_open_prs_details = []
        all_pr_response = read_url(GITHUB_API_LINK)
        for each_object in all_pr_response:
            repos_with_open_prs = read_url(f"{each_object['url']}/pulls")
            for each_object_ in repos_with_open_prs:
                if len(each_object_) != 0:
                    repos_with_open_prs_details.append(
                        {each_object_["html_url"]: each_object_["url"]}
                    )
        json_prs = json.dumps(repos_with_open_prs_details)
        create_and_populate_table = PostgresOperator(
            task_id = "create_and_populate_table",
            postgres_conn_id = "postgres_db",
            sql = f"""
                CREATE TABLE IF NOT EXISTS pr(name VARCHAR);
                INSERT INTO pr (name)
                VALUES ('{json_prs}')
            """
        )
        create_and_populate_table.execute(dict())

    @task
    def consolidate_pull_requests(pr_list):
        from helper_functions import get_timestamps, filter_timestamps_by_latest_time, sort_timestamps, get_top_five_prs
        timestamps = get_timestamps(pr_list)
        filtered_timestamps = filter_timestamps_by_latest_time(timestamps)
        sorted_timestamps = sort_timestamps(filtered_timestamps)
        top_prs = get_top_five_prs(sorted_timestamps)

        links = []
        for each_dict in top_prs:
            links.append(list((each_dict.keys()))[0])
        return "\n\n".join(links)

    @task
    def send_email(message):
        import smtplib
        from email.mime.text import MIMEText
        SMTP_SERVER = Variable.get("SMTP_SERVER")
        SMTP_PORT = Variable.get("SMTP_PORT")
        SENDER_EMAIL_ADDRESS = Variable.get("SENDER_EMAIL_ADDRESS")
        RECEIPIENT_EMAIL_ADDRESS = Variable.get("RECEIPIENT_EMAIL_ADDRESS")
        SMTP_PASSWORD = Variable.get("SMTP_PASSWORD")
        
        subject = "Urgent pull requests that need attention"
        body = message

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL_ADDRESS
        msg["To"] = RECEIPIENT_EMAIL_ADDRESS

        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()
        smtp.login(SENDER_EMAIL_ADDRESS, SMTP_PASSWORD)
        smtp.sendmail(SENDER_EMAIL_ADDRESS, RECEIPIENT_EMAIL_ADDRESS, msg.as_string())
        smtp.quit()

    pr_list = get_all_open_prs()
    message = consolidate_pull_requests(pr_list)
    send_email(message)
    

pr_filter()