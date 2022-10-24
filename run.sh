#!/bin/bash
sudo docker-compose down
if [ -d ./dags/__pycache__ ]
then
    sudo rm -r ./dags/__pycache__
fi
if [ -d logs ]
then
    sudo rm -r logs
    sudo mkdir ./logs
else
    sudo mkdir ./logs
fi
if [ -d plugins ]
then
    sudo rm -r plugins
    sudo mkdir ./plugins
else
    sudo mkdir ./plugins
fi
sudo python3 setup.py develop
sudo docker-compose up