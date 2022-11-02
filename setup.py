from setuptools import setup, find_packages

setup(name = "dags with airflow", packages=find_packages(include=['dags', 'logs', 'plugins']))