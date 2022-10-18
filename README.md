DAGs with Airflow (286)
For raw project instructions see: http://syllabus.africacode.net/projects/dags-with-airflow/


- From the docker directory, run the following commands:

```
mkdir -p ./dags ./logs ./plugins
```
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
```
docker-compose up airflow-init
```