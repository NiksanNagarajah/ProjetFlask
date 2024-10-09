from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)


import os.path
from flask_sqlalchemy import SQLAlchemy

def mkpath(p):
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), 
            p)
        )

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + mkpath('../SQLAlchemy.db')
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'c16b4688-e4ef-44df-8757-dcb88f0da0eb'

from flask_login import LoginManager
login_manager = LoginManager(app)

login_manager.login_view = 'login'

