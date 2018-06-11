from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.api import app as api_blueprint
from app.db import db
from app.config import DB_PATH,UPLOAD_FOLDER

def create_app():
    app = Flask(__name__)
    dbPath = DB_PATH
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(dbPath)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    app.register_blueprint(api_blueprint)

    return app
