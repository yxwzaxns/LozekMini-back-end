# LozekMini-back-end
[front-end](https://github.com/woshicm/LozekMiniProgram.git)
## 认证相关
进入小程序后会检查是否存在 token

1. 如果不存在则使用 login() 获取 token

2. 如果存在则使用 wx.checkSession() 检查用户会话是否过期
    * 如果会话过期则使用 login() 刷新后台会话，并且更新 token
    * 如果会话没过期则认证流程结束

在以后访问后台API接口时，需要在请求 header 里设置认证字段：

token:[token]

## API 相关
##### API 接口列表:

/login

## 后台部署相关
```
git clone https://github.com/yxwzaxns/LozekMini-back-end.git
cd LozekMini-back-end
pip install -r requirements.txt
export FLASK_DEBUG=1
export FLASK_APP=main.py
export FLASK_ENV=development
# 初始化数据库（开发环境使用sqlite）需要在app/config.py中修改数据库信息
python3 manage.py
flask run -p 8000
```



If the modification is not too big (e.g. change the length of a varchar), you can dump the db, manually edit the database definition and import it back again:

echo '.dump' | sqlite3 test.db > test.dump
then open the file with a text editor, search for the definition you want to modify and then:

cat test.dump | sqlite3 new-test.db
