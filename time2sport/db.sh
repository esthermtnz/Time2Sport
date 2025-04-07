#!/bin/bash

rm -rf db.sqlite3 */migrations/0*
python3 manage.py makemigrations
python3 manage.py migrate
python3 populate.py
