DAGs with Airflow (286)
For raw project instructions see: http://syllabus.africacode.net/projects/dags-with-airflow/

- From the main directory of the project, run the following commands:

```
pip install -r requirements.txt
```

```
echo -e "AIRFLOW_UID = $(id -u)\nAIRFLOW_GID=0" > .env
```

- Sign up for SendinBlue (https://www.sendinblue.com/). You can sign up for the free plan.
- Once you are logged in click on the “Transactional” tab at the top of the page. You’ll see some SMTP settings

- Now run the webserver

```
docker-compose up airflow-webserver
```

- you will find the airflow webapp runninng on localhost:8080/
- The default login for the as defined in the docker-compose file is as follows(you may change it if necessary):

```
username: airflow
password: airflow
```

- in the app, navigate to Admin > Variables
- this is where you will be able to add the necessary enviroment variables:

```
TOKEN : <your github token>
USERNAME : <your github username>
SMTP_SERVER : smtp-relay.sendinblue.com
SMTP_PORT : 587
SMTP_PASSWORD : <your smtp password>
SENDER_EMAIL_ADDRESS : <the email address sending the email>
RECEIPIENT_EMAIL_ADDRESS : <the email address receiving the email>
```

- now stop the webserver

- Then run:

```
chmod u+x run.sh
./run.sh
```

- Once docker is done setting up, you can go to the UI by typing the following on your browser:

```
http://localhost:8080/
```
