from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask import session
# 使用flask扩展包，保存用户的登录信息在redis数据库中.
from flask_session import Session

app=Flask(__name__)
app.config.from_object(Config)
# 配置数据库的连接
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:Mysql@123@localhost/python5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)
Session(app)

@app.route('/')
def index():
    session['name']='2018'
    return 'hello world'

if __name__ == '__main__':
    app.run()