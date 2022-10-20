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

```
docker-compose up airflow-init
```
