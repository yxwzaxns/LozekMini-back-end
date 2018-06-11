import requests
from app.config import WX_API,APP_ID,APP_SECRET

def getUserInfo(code):
    url = "{}?appid={}&secret={}&js_code={}&grant_type=authorization_code".format(WX_API,APP_ID,APP_SECRET,code)
    res = requests.get(url).json()
    return str(res['session_key']), str(res['openid'])
