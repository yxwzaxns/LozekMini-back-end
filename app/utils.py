import os
import hashlib
import time
import datetime
import base64
from flask import url_for
from time import gmtime, strftime
from PIL import Image,ImageFilter,ImageFont,ImageDraw,ImageColor
from app.config import UPLOAD_ALLOWED_EXTENSIONS,APP_PORT,APP_DOMAIN,APP_PROTOCOL,THUMBNAIL_SIZE,UPLOAD_FOLDER,THUMBNAIL_FOLDER
from app.config import COMPOSITE_IMAGE_FOLDER, UPLOAD_TMP_FOLDER
from app.config import TENCENT_AI_API_ID,TENCENT_AI_API_KEY
from app.tencent_ai_api import TCAI
from app.other_api import getWeather as _getWeather
from app.other_api import getLocationInfo as _getLocationInfo
from app.other_api import queryWord


DAY = 24*60*60

APP_HOST = APP_PROTOCOL + '://' + APP_DOMAIN + ':' + APP_PORT

def calculateHashCodeForString(string, method='md5'):
    return getattr(hashlib, method)(string.encode('utf8')).hexdigest()

def str2base64(s):
    return base64.b64encode(s.encode()).decode()

def base642str(s):
    return base64.b64decode(s.encode()).decode()

def getMilliTime():
    return int(round(time.time() * 1000))

def getSecondTime():
    return int(round(time.time()))

def allowedUploadFileType(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in UPLOAD_ALLOWED_EXTENSIONS

def getDayName(timestamp,type='mini'):
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    days_mini = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    if type=='mini':
        return days_mini[datetime.datetime.fromtimestamp(int(timestamp)).weekday()]
    else:
        return days[datetime.datetime.fromtimestamp(int(timestamp)).weekday()]

def getTimeFromTimestamp(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))

def getZeroTime(timestamp):
    return int(datetime.date.fromtimestamp(int(timestamp)).strftime("%s"))

def getDateFromTimestamp(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).isoformat()

def getTextTime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def getCurrentTime():
    return getTimeFromTimestamp(getSecondTime())

def createMiniImage(image_name):
    # outfileName = os.path.splitext(infile)[0] + ".thumbnail" + os.path.splitext(infile)[1]
    outfilePath = os.path.join(THUMBNAIL_FOLDER,image_name)
    try:
        with Image.open(os.path.join(COMPOSITE_IMAGE_FOLDER,image_name)) as im:
            im.thumbnail(THUMBNAIL_SIZE)
            im.save(outfilePath, "PNG")
    except IOError:
        print("cannot create thumbnail for", outfilePath)
    return outfilePath

def fileExist(filePath):
    return os.path.isfile(filePath)

def createFilteredImage(filename,ft):
    t_ai = TCAI(TENCENT_AI_API_ID, TENCENT_AI_API_KEY)
    image_path = os.path.join(UPLOAD_TMP_FOLDER,filename)
    filteredImagePath = os.path.join(UPLOAD_TMP_FOLDER,filename + '_' + str(ft))
    with open(image_path,'rb') as f:
        img = f.read()
    rsp = t_ai.getImageFilter(img,ft)
    if rsp['ret'] == 0:
        image = base64.b64decode(rsp['data']['image'])
        with open(filteredImagePath,'wb') as f:
            f.write(image)
        return 0
    else:
        # print(json.dumps(rsp, ensure_ascii=False, sort_keys=False, indent=4))
        return rsp['msg']
def getUploadPath(filename):
    return os.path.join(UPLOAD_FOLDER, filename)

def getTmpPath(filename):
    return os.path.join(UPLOAD_TMP_FOLDER, filename)

def createImageUrl(filename):
    return APP_HOST + url_for('app.getImage',name=filename) + '&' + str(getSecondTime())

def getFileType(filename):
    return filename.rsplit('.', 1)[1]

def convertImageTo(src_path,des_path,ctype='PNG'):
    Image.open(src_path).convert('RGBA').save(des_path,ctype)

def getWeather(location):
    weather = _getWeather(location)['HeWeather6'][0].get('now','')
    return weather

def getWord(word):
    return queryWord(word)['result']

def getLocationInfo(lat,lng):
    return _getLocationInfo(lat,lng)
