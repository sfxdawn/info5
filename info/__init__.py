from flask import Flask
from flask_session import Session
from config import config
from flask_sqlalchemy import SQLAlchemy


# 先实例化sqlalchemy对象
db=SQLAlchemy()

# 工厂函数: 让app 通过函数来调用可以根据传入的参数的不同,动态的生产不同情况下的app
def create_app(config_name):
	app=Flask(__name__)
	# 获取配置参数的名称:
	app.config.from_object(config[config_name])
	db.init_app(app)     # 这句代码就等效于 db=SQLAlchemy(app) 这叫把app和程序实例进行关联
						# 但是这句话还有一个作用,就是app一创造出来,就和db关联了,现在db已经和app关联了.
	Session(app)
	return app

