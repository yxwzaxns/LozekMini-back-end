from flask import g,url_for
from flask_sqlalchemy import SQLAlchemy
from app import utils
import os,copy,json
from app.db import db


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
    # email = Column(String(50))
    # password = Column(String(50))
    # createtime = Column(String(30))
    # lastlogintime = Column(String(30))
    # active = Column(Integer, DefaultClause('1')) # 1 : active ; 0 disable
    # pubkey = Column(Text())

def addTextDiaryImage(image,did):
    filename = utils.str2base64(image.filename)
    # filehash = utils.calculateHashCodeForString(image.filename,'sha1')
    # type = image.filename.rsplit('.', 1)[1]
    filename = filename + '_textImage'
    filepath = utils.getUploadPath(filename)
    if not utils.fileExist(filepath):
        image.save(filepath)
    diaryImage = DiaryImage(
        did= did,
        image= filename
    )
    db.session.add(diaryImage)
    db.session.commit()
    return 0

def getDiaryById(did):
    data = []
    diary_tpl = {'diary':{'text':[],'image':[]},'date':[]}
    # diary = Diary.query.filter_by(uid=g.uid).filter_by(id=did).first()
    diary = Diary.query.filter_by(id=did).first()
    if diary:
        day = utils.getDayName(diary.create_time)
        createTime = utils.getTimeFromTimestamp(diary.create_time)
        if diary.diary_type == 0: # text diary
            images = ''
            diaryImages = diary.images.all()
            if len(diaryImages) != 0:
                images = [{'url':utils.createImageUrl(i.image) + '&type=text_diary_image'} for i in diaryImages]
            lastModifiedTime = utils.getTimeFromTimestamp(diary.last_modified_time)
            d = {
                'main': {
                    'id':diary.id,
                    'title':diary.title,
                    'text':diary.content,
                    'images': images,
                },
                'extra': {},
                'system': {
                    'createdTime': [
                        createTime.year,
                        createTime.month,
                        createTime.day,
                        createTime.hour,
                        createTime.minute,
                        createTime.second,
                        day
                    ],
                    'lastModifiedTime': diary.last_modified_time,
                    'weather': diary.weather
                }
            }
            diary_tpl['diary']['text'].append(d)
        else:
            actions = json.loads(diary.additional_actions)
            imageText = actions[1].get('text','NULL')
            d = {'id':diary.id,
                 'imageURL': utils.createImageUrl(diary.image),
                 'text': imageText,
                 'createtime':[createTime.year,
                               createTime.month,
                               createTime.day,
                               createTime.hour,
                               createTime.minute,
                               createTime.second,
                               day
                               ]}
            diary_tpl['diary']['image'].append(d)
        diary_tpl['date']=[
            createTime.year,
            createTime.month,
            createTime.day,
            day
        ]
        data.append(diary_tpl)
    return data

def getDiary(get_end_time,max_diary_count=10):
    data = []
    day_count = 0
    diary_tpl = {'diary':{'text':[],'image':[]},'date':[]}
    reference_time = ''
    end_time = utils.getSecondTime()
    if get_end_time != '':
        end_time = int(get_end_time)
    diarys = Diary.query.filter_by(uid=g.uid) \
                        .filter(Diary.create_time < end_time) \
                        .filter_by(is_delete=0) \
                        .order_by(Diary.create_time.desc()) \
                        .limit(max_diary_count) \
                        .all()
    print('total {} diary be select !!!!!!!'.format(len(diarys)))
    if len(diarys) != 0:
        reference_time = utils.getZeroTime(diarys[0].create_time)
        for diary in diarys:
            while True:
                if diary.create_time < reference_time:
                    if diary_tpl['date'] != []:
                        data.append(copy.deepcopy(diary_tpl))
                        diary_tpl['diary']['text'] = []
                        diary_tpl['diary']['image'] = []
                        diary_tpl['date'] = []
                    reference_time -= utils.DAY
                    day_count += 1
                else:
                    break

            createTime = utils.getTimeFromTimestamp(diary.create_time)
            day = utils.getDayName(diary.create_time)
            if diary.diary_type == 0: # text diary
                images = ''
                diaryImages = diary.images.all()
                if len(diaryImages) != 0:
                    images = [{'url':utils.createImageUrl(i.image) + '&type=text_diary_image'} for i in diaryImages]
                lastModifiedTime = utils.getTimeFromTimestamp(diary.last_modified_time)
                d = {
                    'main': {
                        'id':diary.id,
                        'title':diary.title,
                        'text':diary.content,
                        'images': images,
                    },
                    'extra': {},
                    'system': {
                        'createdTime': [
                            createTime.year,
                            createTime.month,
                            createTime.day,
                            createTime.hour,
                            createTime.minute,
                            createTime.second,
                            day
                        ],
                        'lastModifiedTime': diary.last_modified_time,
                        'weather': diary.weather
                    }
                }
                diary_tpl['diary']['text'].append(d)
            else:
                actions = json.loads(diary.additional_actions)
                imageText = actions[1].get('text','NULL')
                d = {'id':diary.id,
                     'imageURL': utils.createImageUrl(diary.image),
                     'text': imageText,
                     'createtime':[createTime.year,
                                   createTime.month,
                                   createTime.day,
                                   createTime.hour,
                                   createTime.minute,
                                   createTime.second,
                                   day
                                   ]}
                diary_tpl['diary']['image'].append(d)
            diary_tpl['date']=[
                createTime.year,
                createTime.month,
                createTime.day,
                day
            ]

        if day_count == 0:
            data.append(diary_tpl)
        data.reverse()
    return data
