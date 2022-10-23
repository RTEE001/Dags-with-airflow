DAGs with Airflow (286)
For raw project instructions see: http://syllabus.africacode.net/projects/dags-with-airflow/

- From the main directory, run the following commands:

```
pip install -r requirements.txt
```

```
mkdir -p ./logs ./plugins
```

```
echo -e "AIRFLOW_UID = $(id -u)\nAIRFLOW_GID=0" > .env
```

- Sign up for SendinBlue (https://www.sendinblue.com/). You can sign up for the free plan.
- Once you are logged in click on the “Transactional” tab at the top of the page. You’ll see some SMTP settings

- Create a bash script and name it 'env.sh' and put in the following variables:

```
#!/bin/sh

export TOKEN=<your github token>
export USERNAME=<your github username>
export SMTP_SERVER=<smtp server value from sendinblue>
export SMTP_PORT=<smtp port from sendinblue>
export SENDER_EMAIL_ADDRESS=<email address you used in sendinblue>
export RECEIPIENT_EMAIL_ADDRESS=<email address of the receipient>
export SMTP_PASSWORD=<your sendinblue password from the settings>
```

- Source the bash script by running:

```
source env.sh
```

- Then run:

```
docker-compose up airflow-init
```

```
docker-compose up
```

- Once docker is done setting up, you can go to the UI by typing the following on your browser:

```
http://localhost:8080/
```
