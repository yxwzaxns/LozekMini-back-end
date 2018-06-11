from functools import wraps
from flask import request, abort ,g
from app.db import db
from app.db.user import User
from app.config import TOKEN_TIMEOUT,NO_AUTH
from app import utils

def hasPermit():
    if NO_AUTH:
        g.uid = '9de16f130c7b74764c687cffa85dce49'
        return True
    token=request.headers.get('token',None)
    if token is None:
        return False
    user = User.query.filter_by(token=request.headers['token']).first()
    if user is not None:
        if user.expiration_time > utils.getSecondTime():
            # update token expiration time
            user.expiration_time = utils.getSecondTime() + TOKEN_TIMEOUT
            db.session.commit()
            g.uid = user.openid
            return True
    return False
