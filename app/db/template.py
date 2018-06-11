from app.db import db

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
