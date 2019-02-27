from flask import Flask
from flask_session import Session
from config import Config,config
from flask_sqlalchemy import SQLAlchemy


# 工厂函数: 让app 通过函数来调用可以根据传入的参数的不同,动态的生产不同情况下的app
db=SQLAlchemy()
def create_app(config_name):
	app=Flask(__name__)
	# 获取配置参数的名称:
	app.config.from_object(config[config_name])
	Session (app)
	db.init_app (app)
	return app

