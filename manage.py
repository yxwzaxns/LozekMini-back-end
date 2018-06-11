from app.config import DB_PATH
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json,sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DB_PATH)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(30),unique=True,nullable=False)
    session_key = db.Column(db.String(30),nullable=False)
    token = db.Column(db.String(32),nullable=True)
    expiration_time = db.Column(db.Integer,nullable=False)

    # id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(80), unique=True, nullable=False)
    # email = db.Column(db.String(120), unique=True, nullable=False)

class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(30),nullable=False)
    diary_type = db.Column(db.Integer,nullable=False)# 1 image 0 Text
    title = db.Column(db.String(20))
    content = db.Column(db.Text)
    image = db.Column(db.String(50))
    additional_actions = db.Column(db.Text)
    location = db.Column(db.String(50))
    weather = db.Column(db.String(20))
    create_time = db.Column(db.Integer,nullable=False)
    last_modified_time = db.Column(db.Integer,nullable=False)
    has_image = db.Column(db.Integer)
    is_delete = db.Column(db.Integer)
    images = db.relationship('DiaryImage', backref='diary', lazy='dynamic')

class DiaryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    did = db.Column(db.Integer, db.ForeignKey('diary.id'),nullable=False)
    image = db.Column(db.String(50))

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

def initDB():
    # db.drop_all()
    db.create_all()

def addTemplate():
    template = Template()
    tpl = {'nodes': "<div style=' align-items: center; color: {color}; transform: scale({fontSize}, {fontSize});width: 140px; height: 170px; text-align: left;display: flex;flex-direction:row-reverse; align-items: center; justify-content: center;'><div style='height: 100%;width: 15%;display: flex; justify-content: center; flex-direction:column; font-size: 20px; opacity: 0.8;'>{sourceText.title}</div><div style='width: 2px; height: 150px; opacity: 0.8; background-color: {color}; margin-left: 10px; margin-right: 5px;'></div><div style='font-size: 15px; height: 100%;width: 80%; writing-mode: vertical-rl;text-align: left; letter-spacing: 2px; line-height: 20px;'>{sourceText.text}</div>",
         'systemVariable': {'defaultValue': '让时间停在这一刻',
          'id': 0,
          'height': 170,
          'width': 140,
          'hasTime': False,
          'time': '',
          'hasLocation': False,
          'marginLeft': 8,
          'marginTop': 0,
          'maxLength': 50,
          'keyWords': []},
         'userVariable': {'color': 'color', 'fontSize': 'fontSize'}}

    template.content = json.dumps(tpl)
    db.session.add(template)
    db.session.commit()

if __name__ == '__main__':
    # initDB()
    cmd = sys.argv[1]

    if cmd == 'init':
        print("init db")
        initDB()
    elif cmd == 'tpl':
        addTemplate()
    else:
        pass
