from flask import Blueprint,abort,url_for,send_file,g
from flask import request
from flask import jsonify
from app.weixin_api import getUserInfo
from app.db.user import User
from app.db.template import Template
from app.db.diary import Diary,getDiary,addTextDiaryImage,getDiaryById
from app.db import db
from app.auth import hasPermit
from app.config import TOKEN_TIMEOUT,UPLOAD_ALLOWED_EXTENSIONS,UPLOAD_FOLDER,APP_DOMAIN,MAX_DIARY_COUNT,THUMBNAIL_FOLDER,COMPOSITE_IMAGE_FOLDER
from app.config import IMAGE_NOT_FOUND, UPLOAD_TMP_FOLDER, NOT_AUTH
from app import utils
from app.image_methods import compositeImage
import os,copy,json
from threading import Thread

app = Blueprint('app', __name__, url_prefix='')

@app.before_request
def before_request():
    if request.path not in NOT_AUTH and not hasPermit():
        abort(403)

@app.route('/')
def index():
    return "ok"

@app.route('/ping')
def ping():
    return 'ok'

@app.route('/login',methods=['POST'])
def login():
    content = request.get_json()
    code =  str(content['code'])
    sessionKey,openid = getUserInfo(code)
    res = User.query.filter_by(openid=openid).first()
    # 如果没有查询到用户id，则注册一个新的用户
    if res is None:
        u = User(
                openid = openid,
                session_key = sessionKey,
                token = "",
                expiration_time = utils.getSecondTime() + TOKEN_TIMEOUT
                )
        db.session.add(u)
        db.session.commit()

    # 为用户生成token
    token = utils.calculateHashCodeForString(openid + str(utils.getMilliTime()))
    res = User.query.filter_by(openid=openid).first()
    if res is not None:
        res.token = token
        res.expiration_time = utils.getSecondTime() + TOKEN_TIMEOUT
        db.session.commit()

    return jsonify(token=token)

@app.route('/parsetext', methods=['POST'])
def parsetext():
    content = request.get_json()
    text = content['text']
    return jsonify(text= text+'hahaha')

@app.route('/upload_with_filter',methods=['POST'])
def upload_with_filter():
    content = request.get_json()
    # save remote image to local
    image_url = content.get('imageURL','')
    filename = image_url[image_url.index('name')+5:-4]
    filepath = utils.getTmpPath(filename)
    if not utils.fileExist(filepath):
        return jsonify(status=0,msg='filter image not exist')
    new_image_path = utils.getUploadPath(filename)
    utils.convertImageTo(filepath,new_image_path)
    diary = Diary(
        uid = g.uid,
        diary_type = 1,
        image = filename,
        additional_actions = json.dumps(content['actions']),
        location = content['location'],
        create_time = utils.getSecondTime(),
        last_modified_time = '',
        is_delete = 0
    )

    db.session.add(diary)
    db.session.commit()
    # create image diary with additional_actions
    actions = content['actions']
    compositeImage(filename,actions)
    # create thumbnail image for it
    utils.createMiniImage(filename)
    return jsonify(imgUrl=url_for('app.getImage',name=filename))

@app.route('/upload',methods=['POST'])
def upload():
    image = request.files['image']
    if image and utils.allowedUploadFileType(image.filename):
        # check if the image belong to the text diary
        diaryID = request.form.get('id','')
        if diaryID != '':
            res = addTextDiaryImage(image,diaryID)
            if res == 0:
                return jsonify(status=1)
            else:
                return jsonify(status=0,msg=res)
        filehash = utils.calculateHashCodeForString(image.filename,'sha1')
        # type = image.filename.rsplit('.', 1)[1]
        filename = filehash
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        # if utils.fileExist(filepath):
        #     return jsonify(status=0,msg='diary has been created!')
        image.save(filepath)


    diary = Diary(
        uid = g.uid,
        diary_type = 1,
        image = filename,
        additional_actions = request.form.get('actions',''),
        location = request.form.get('location',''),
        create_time = utils.getSecondTime(),
        last_modified_time = '',
        is_delete = 0
    )

    db.session.add(diary)
    # create image diary with additional_actions
    actions = json.loads(request.form['actions'])
    compositeImage(filename,actions)
    # create thumbnail image for it
    utils.createMiniImage(filename)
    db.session.commit()
    return jsonify(imgUrl=url_for('app.getImage',name=filename))


@app.route('/image')
def getImage():
    filename = request.args.get("name")
    token = request.args.get("token")
    imageType = request.args.get("type")
    if imageType == 'origin':
        print('origin')
        image_path = os.path.join(COMPOSITE_IMAGE_FOLDER,filename)
        if not utils.fileExist(image_path):
            image_path = IMAGE_NOT_FOUND
        return send_file(image_path)
    elif imageType == 'text_diary_image':
        print('text_diary_image')
        image_path = utils.getUploadPath(filename)
        if not utils.fileExist(image_path):
            image_path = IMAGE_NOT_FOUND
        imageType = utils.getFileType(utils.base642str(filename[0:-10]))
        return send_file(image_path,mimetype=imageType)
    else:
        miniImage = os.path.join(THUMBNAIL_FOLDER,filename)
        if not utils.fileExist(miniImage):
            utils.createMiniImage(filename)
        return send_file(miniImage,mimetype='png')

@app.route('/diary',methods=['POST','GET'])
def diary():
    if request.method == 'POST':
        content = request.get_json()
        if content.get('id','') != '':
            diary = Diary.query.get(int(content['id']))
            diary.title = content.get('title','')
            diary.content = content.get('text','')
            diary.weather = content.get('weather','')
            diary.has_image = content.get('has_image','')
            diary.last_modified_time = utils.getSecondTime()
            try:
                db.session.commit()
            except Exception as e:
                print(e)
        else:
            diary = Diary(
                uid = g.uid,
                diary_type = 0,
                title = content.get('title',''),
                content = content.get('text',''),
                has_image = content.get('has_image',''),
                location = content.get('location',''),
                weather = content.get('weather',''),
                create_time = utils.getSecondTime(),
                last_modified_time = utils.getSecondTime(),
                is_delete = 0
            )
            db.session.add(diary)
            db.session.commit()

        return jsonify(status='1',id=diary.id)
    else:
        did = request.args.get('id',0)
        print(did)
        if  int(did) != 0:
            data = getDiaryById(did)
        else:
            data = getDiary(request.args.get("end_time",''),max_diary_count=MAX_DIARY_COUNT)
        return jsonify(diary=data)

@app.route('/delete_diary')
def deleteDiary():
    diaryID = request.args.get('id','')
    if diaryID != '':
        try:
            diary = Diary.query.get(diaryID)
            if diary:
                diary.is_delete = 1
                db.session.commit()
                return jsonify(status='ok',id=diaryID)
        except Exception as e:
            return jsonify(status=e)
    return jsonify(status='need id')

@app.route('/filter',methods=['POST','GET'])
def imageFilter():
    if request.method != 'POST':
        filename = request.args.get("name")
        imageType = filename.rsplit('.', 1)[1]
        image_path = os.path.join(UPLOAD_TMP_FOLDER,filename.rsplit('.', 1)[0])
        return send_file(image_path,mimetype=imageType)
    else:
        image = request.files['image']
        if image and utils.allowedUploadFileType(image.filename):
            imageType = image.filename.rsplit('.', 1)[1]
            filehash = utils.calculateHashCodeForString(image.filename,'sha1')
            filename = filehash
            filepath = os.path.join(UPLOAD_TMP_FOLDER, filename)
            if not utils.fileExist(filepath):
                image.save(filepath)

        filterID = request.form['type']
        preFilter = request.form.get('all',0)
        if int(preFilter) == 0:
            # check if the filter image has been created
            filteredImagePath = filepath + '_' + filterID
            if utils.fileExist(filteredImagePath):
                url = utils.APP_HOST + url_for('app.imageFilter',name=filename + '_' + str(filterID) + '.' + imageType)
                return jsonify(status=1,imgUrl=url)
            res = utils.createFilteredImage(filename,filterID)
            if res == 0:
                url = utils.APP_HOST + url_for('app.imageFilter',name=filename + '_' + str(filterID) + '.' + imageType)
                return jsonify(status=1,imgUrl=url)
            else:
                return jsonify(status=0,msg=res)
        else:
            # thread.start_new_thread( invokeFilter, (filepath,))
            Thread(target=invokeFilter,args=(filepath,filename,)).start()
            return jsonify(status=1)

def invokeFilter(filepath,filename):
    # create all filter image
    for t in [i+1 for i  in range(3)]:
        filteredImagePath = filepath + '_' + str(t)
        if utils.fileExist(filteredImagePath):
            continue
        else:
            utils.createFilteredImage(filename,t)

@app.route('/filter1',methods=['POST','GET'])
def imageFilter1():
    if request.method != 'POST':
        pass
    else:
        image = request.files['image']
        filterID = request.form['type']
        # print(request.form)
        return jsonify(name=image.filename,id=filterID)

@app.route('/template')
def template():
    templates = Template.query.all()
    data = []
    defaultTemplate = {
        "nodes": "<div style='align-items: center; color:{color}; transform: scale({fontSize},{fontSize});width: 126px; height: 84px; padding: 0px; text-align: center;'><div style='font-size: 39px; letter-spacing: 3px; height: 60%;'>{lozek-time}</div><div style='letter-spacing: 2px; height: 20%; font-size: 12px; margin:0px;'>{sourceText}</div><div style='font-size: 8px; margin:0px;padding: 0px;height: 20%'>Let time stop at this moment</div></div>",
        "systemVariable": {
          "defaultValue": "让时间停在这一刻",
          "id": 0,
          "height": 84,
          "width": 126,
          "hasTime": True,
          "time": '',
          "hasLocation": False,
          "marginLeft": 8,
          "marginTop": 6,
          "maxLength": 8,
          "keyWords": [],
        },
        "userVariable": {
          "color": "color",
          "fontSize": "fontSize",
        }
    }
    data.append(defaultTemplate)
    if len(templates) != 0:
        tpl = {}
        for template in templates:
            try:
                tpl = json.loads(template.content)
            except Exception as e:
                print(e)
            data.append(tpl)
    return jsonify(data = data)

@app.route('/get_weather')
def get_weather():
    location = request.args.get("location",'guilin')
    res = utils.getWeather(location)
    return jsonify(status='1',data=res)

@app.route('/get_word')
def get_word():
    word = request.args.get("word",'美好')
    res = utils.getWord(word)
    return jsonify(status='1',data=res)

@app.route('/get_location_info')
def get_location_info():
    lat = request.args.get("lat",'35.658651')
    lng = request.args.get("lng",'139.745415')
    res = utils.getLocationInfo(lat,lng)['result']
    return jsonify(status='1',data=res)

@app.route('/test')
def test():
    # uid = db.Column(db.String(30),nullable=False)
    # type = db.Column(db.Integer(1),nullable=False)# 1 image 0 Text
    # title = db.Column(db.String(20))
    # content = db.Column(db.Text)
    # image_path = db.Column(db.String(50))
    # create_time = db.Column(db.String(10),nullable=False)
    # for i in range(1):
    #     d = Diary(
    #             uid = g.uid,
    #             type = 0,
    #             title = 'hellaongosss'+str(i),
    #             content = 'worlsssd' + str(i),
    #             create_time = utils.getSecondTime() - utils.DAY * 0
    #             )
    #     db.session.add(d)
    #     db.session.commit()
    # im_name = 'fd58d91d929bb245bf510bf6d9a69567b610a800.jpg'
    # actions = [
    # {"action":"text","text":"13:38","position":[132.5,33.2],"font-style":"","font-color":"","font-size":39},
    # {"action":"text","text":"让时间停留在这一刻","position":[132.5,80.30000000000001],"font-style":"","font-color":"","font-size":12},
    # {"action":"text","text":"Let time stop at this moment","position":[132.5,99.10000000000001],"font-style":"","font-color":"","font-size":8}
    # ]
    # composeImage(im_name,actions)
    diary = Diary.query.get(1)
    print(diary.images.all())
    return jsonify(status='ok',res=diary.images.all()[0].image)
