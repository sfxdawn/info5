from flask import Flask
from flask_session import Session
from config import config,Config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
#导入标准日志模块
import logging
# 日志处理模块
from logging.handlers import RotatingFileHandler

#导入flask_wtf 扩展实现的csrf保护和验证
from flask_wtf import CSRFProtect , csrf





# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)
# 先实例化sqlalchemy对象
db=SQLAlchemy()

redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)   # 从数据库里面拿出来是byte类型,要转换,



# 工厂函数: 让app 通过函数来调用可以根据传入的参数的不同,动态的生产不同情况下的app
def create_app(config_name):
	app=Flask(__name__)
	# 获取配置参数的名称:
	app.config.from_object(config[config_name])
	db.init_app(app)     # 这句代码就等效于 db=SQLAlchemy(app) 这叫把app和程序实例进行关联

									# 但是这句话还有一个作用,就是app一创造出来,就和db关联了,现在db已经和app关联了.
	Session(app)
	# 开启csrf保护
	CSRFProtect(app)
	# 生成csrf的口令 token
	@app.after_request
	def after_request(response):
		csrf_token=csrf.generate_csrf()
		# 写入到客户端浏览器的cookie中
		response.set_cookie('csrf_token',csrf_token)
		return response


	#注册蓝图
	from info.modules.index import index_blue
	app.register_blueprint(index_blue)
	from info.modules.passport import passport_blue
	app.register_blueprint(passport_blue)


	#导入自定义的过滤器
	from info.utils.commons import index_filter
	app.add_template_filter(index_filter,'index_filter')

	return app






























