#!/bin/bash                                                                     

virtualenv -p python3 venv
source venv/bin/activate

pip install flask
pip install python-dotenv
pip install bootstrap-flask
pip install PyYAML
pip install flask-sqlalchemy
pip install flask-wtf
pip install flask-login



