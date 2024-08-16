#!/bin/bash

workTree=/home/mmd/sobhan/server

echo "---Activating virtualenv..."
source /home/mmd/sobhan/env/bin/activate

echo "---Running jobs..."
cd $workTree
python manage.py runjobs minutely

echo "---Done..."