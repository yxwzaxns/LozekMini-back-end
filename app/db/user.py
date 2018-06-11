from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(30),unique=True,nullable=False)
    session_key = db.Column(db.String(30),nullable=False)
    token = db.Column(db.String(32),nullable=True)
    expiration_time = db.Column(db.Integer,nullable=False)
    # email = Column(String(50))
    # password = Column(String(50))
    # createtime = Column(String(30))
    # lastlogintime = Column(String(30))
    # active = Column(Integer, DefaultClause('1')) # 1 : active ; 0 disable
    # pubkey = Column(Text())

    def tokenExpired():
        return False
