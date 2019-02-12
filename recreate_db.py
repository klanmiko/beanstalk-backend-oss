from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from run import create_app
from Model import User

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
db.drop_all()
db.create_all()