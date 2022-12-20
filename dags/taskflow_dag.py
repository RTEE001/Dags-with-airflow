from airflow.models import Variable
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
import json

GITHUB_API_LINK = "https://api.github.com/user/repos?per_page=100"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 10, 1),
}


@dag(
    schedule=timedelta(minutes=20),
    default_args=default_args,
    catchup=False,
    description="notifies the user which pull requests need attention",
    tags=["pr"],
)
def pr_filter():
    @task
    def get_all_open_prs():
        from helper_functions import read_url, create_and_populate_table_pr

        all_pr_response = read_url(GITHUB_API_LINK)
        for each_object in all_pr_response:
            repos_with_open_prs = read_url(f"{each_object['url']}/pulls")
            for each_object_ in repos_with_open_prs:
                if len(each_object_) != 0:
                    create_table = PostgresOperator(
                        task_id="create_table",
                        postgres_conn_id="postgres_db",
                        sql=create_and_populate_table_pr(
                            each_object_["html_url"], each_object_["url"]
                        ),
                    )
                    create_table.execute(dict())

    @task
    def get_timestamps():
        from helper_functions import extract_prs_from_db, read_url, timestamps

        reviews = extract_prs_from_db("reviews_url")
        reviews = list(sum(reviews, ()))

        for reviewed_pr in reviews:
            comments = read_url(reviewed_pr)
            if len(comments) == 0:
                url = read_url(reviewed_pr.rsplit("/", 1)[0])
                if url["updated_at"] != None:
                    timestamps(url["html_url"], url["updated_at"])
                else:
                    timestamps(url["html_url"], url["created_at"])
            else:
                for k in comments:
                    timestamps(
                        k["_links"]["html"]["href"].split("#", 1)[0], k["submitted_at"]
                    )

    @task
    def send_email():

        from helper_functions import get_top_5_prs
        import smtplib
        from email.mime.text import MIMEText

        SMTP_SERVER = Variable.get("SMTP_SERVER")
        SMTP_PORT = Variable.get("SMTP_PORT")
        SENDER_EMAIL_ADDRESS = Variable.get("SENDER_EMAIL_ADDRESS")
        RECEIPIENT_EMAIL_ADDRESS = Variable.get("RECEIPIENT_EMAIL_ADDRESS")
        SMTP_PASSWORD = Variable.get("SMTP_PASSWORD")

        subject = "Urgent pull requests that need attention"
        message = get_top_5_prs()
        message = "\n".join([str(x) for t in message for x in t])
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

    get_all_open_prs() >> get_timestamps() >> send_email()


pr_filter()
