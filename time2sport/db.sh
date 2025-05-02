#!/bin/bash


find . -path "*/migrations/0*.py" -delete
find . -type d -path "*/migrations/__pycache__" -exec rm -rf {} +

psql -U alumnodb -h localhost -d postgres -c "DROP DATABASE IF EXISTS time2sport;"
psql -U alumnodb -h localhost -d postgres -c "CREATE DATABASE time2sport OWNER alumnodb;"

python3 manage.py makemigrations
python3 manage.py migrate
python3 populate.py
