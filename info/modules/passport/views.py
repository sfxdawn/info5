from flask import request, jsonify, current_app, make_response, session
import random
from info.libs.yuntongxun import sms
from . import passport_blue
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,db
# 导入模型类
from info.models import User
import re
from datetime import datetime

"""
json.loads:把json字符串转成字典
	json.dumps: 把字典转成json字符串
	json.load/json.dump(操作的是文件对象)
	var data={
	"mobile":mobile,
	"image_code":imagecode,
	...
	}
	a='123';
	json的概念:本质字符串,基于键值对的字符串;轻量级的数据交互格式;
	json的作用:实现跨语言,跨平台的数据交互;
	xml 格式: 作用是用来传输数据;都是闭合标签
	XML: xmltodic模块,xmltodict.parse()/unparse()  微信,
	html用来展示数据;
	<xml>
		<mobile>12223234</mobile>
		<image_code>12223234</image_code>
	</xml>

	JSON
	{
		"mobile":mobile,
			"image_code":imagecode,
	}

	JSON.Stringify(data) 前端把对象转成json字符串;

"""

@passport_blue.route('/image_code')
def generate_image_code():
	"""
	1.获取前端生成的uuid,/image_code?image_code_id=uuid
		request.args.get('image_code_id')
		 2. 判断参数是否存在,如果不存在uuid,直接return
		 3.调用工具生成图片验证码,
		 4.存储redis图片验证码的text文本,构造redis数据实例,用来存储业务相关的数据比如 :图片验证码
		 5. 返回图片给浏览器,
	状态码:
	return jsonify(errno=666,errmsg='uuid未获取到')
	1. 自定义的状态码: 用来实现前后端的数据交互.
	$.ajax({
		url:'/image_code,
		type:'get'
		data:data,
		contentType:'application/json'
		success:function(resp){
			if (resp == 666){
				alert(成功)
			}else{
				alert(失败)
			}

		}

	})

	:return:
	"""
	# 获取参数
	image_code_id=request.args.get('image_code_id')
	# 校验参数是否存在,如果UUID不存在,返回错误信息
	if not image_code_id:
		return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
	# 调用工具captcha生成图片验证码
	name,text,image=captcha.generate_captcha()
	# 保存图片验证码的文本
	try:
		redis_store.setex('ImageCode_'+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='保存图片验证码失败')
	else:
		response=make_response(image)
		# 默认的响应报文Content-Type:text/html,应该修改默认的响应报文
		response.headers['Content-Type']='image/jpg'

		return response

@passport_blue.route('/sms_code',methods=['POST'])
def send_sms_code():
	"""
	发送短信验证码
	获取参数---校验参数---业务处理(查询数据)---返回结果
	1、获取post请求的三个参数;前端使用ajax传入的参数,前端如何传入json?
		mobile/image_code/image_code_id
		request.json.get()
	2、检查参数的完整性
	3、检查手机号的格式是否符合要求,使用正则
	4、比较图片验证码,从redis数据库中获取真实的图片验证码
		get()
	5、判断图片验证码是否过期
	6、需要先删除Redis中真实存在的图片验证码,因为图片验证码只能获取一次,比较一次.
	7、比较图片验证码,如果图片验证码正确
		**检查手机号是否注册过???
	8、生成短信的随机数,六位数的随机数 random
	9、保存短信随机数到Redis数据库中,
	10、调用云通讯接口,发送短信,保存发送结果
	11、返回发送结果

	:return:
	"""
	mobile=request.json.get('mobile')
	image_code=request.json.get('image_code')
	image_code_id=request.json.get('image_code_id')
	# 检查参数的完整性
	if not all([mobile,image_code,image_code_id]):
		return  jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
	# 检查手机号的格式,13012345678
	if not re.match(r'1[3456789]\d{9}$',mobile):
		return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
	#  尝试从redis数据库中获取真实的图片验证码
	try:
		real_image_code=redis_store.get('ImageCode_'+image_code_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='获取图片验证码数据失败')
	# 判断图片验证码是否过期
	if not real_image_code:
		return jsonify(errno=RET.NODATA,errmsg='图片验证码已过期')
	# 删除Redis数据库中的图片验证码
	try:
		redis_store.delete('ImageCode_'+image_code_id)
	except Exception as e:
		current_app.logger.error(e)
	# 比较图片验证码是否一致,忽略大小写
	if real_image_code.lower() != image_code.lower():
		return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')
	# 确认用户是否注册过?
	try:
		# User.query.filter_by(mobile=mobile).first()
		user=User.query.filter(User.mobile==mobile).first()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')
	else:
		# 判断查询结果是否存在
		if user is not None:
			return jsonify(errno=RET.DATAEXIST,errmsg='用户已存在')
	#生成6位数短信随机数,使用随机数模块
	sms_code='%06d' % random.randint (0, 999999)
	print(sms_code)
	try:
		redis_store.setex('SMSCode_'+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='保存短信数据失败')
	# 调用云通讯扩展,发送短信
	try:
		ccp=sms.CCP()
		result=ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
	# 判断发送是否成功
	if result==0:
		return jsonify(errno=RET.OK,errmsg='发送成功')
	else:
		return jsonify(errno=RET.THIRDERR,errmsg='发送失败')

@passport_blue.route('/register',methods=['POST'])
def register():
	"""
	用户注册
	1、获取参数,mobile,sms_code,password
	2、检查参数的完整性
	3、检查手机号的格式
	4、检查短信验证码,尝试从Redis数据库中获取真实的短信验证码
	5、判断获取结果是否过期
	6、先比较短信验证码是否一致
	7、删除Redis数据库中的短信验证码
	8、构造模型类对象
	user=User()
	user.password=password
	9、提交数据到数据库中,mysql
	10、把用户基本信息缓存到Redis数据库中
	session['user_id']=user.id
	session['mobile']=mobile
	session['nick_name']=mobile
	11、返回结果

	:return:
	"""
	mobile=request.json.get('mobile')
	sms_code=request.json.get('sms_code')
	password=request.json.get('password')

	# 检查参数完整性
	if not all([mobile,sms_code,password]):
		return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
	# 检查手机号格式
	if not re.match(r'1[3456789]\d{9}$',mobile):
		return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
	# 尝试从Redis中获取真实的短信验证码
	try:
		real_sms_code=redis_store.get('SMSCode_'+mobile)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='查询短信验证码失败')
	# 判断查询结果
	if not real_sms_code:
		return jsonify(errno=RET.NODATA,errmsg='短信验证码已过期')
	# 比较短信验证码是否正确
	if real_sms_code !=str(sms_code):
		return jsonify(errno=RET.DATAERR,errmsg='短信验证码不一致')
	# 删除redis数据库中存储的短信验证码
	try:
		redis_store.delete('SMSCode_'+mobile)
	except Exception as e:
		current_app.logger.error(e)
	# 构造模型类对象
	user=User()
	user.mobile=mobile
	user.nick_name=mobile
	# 调用了模型类中的generate_password_hash实现了密码 加密储存,sha256
	user.password=password
	# 提交用户注册信息数据到mysql数据库中
	try:
		db.session.add(user)
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		# 存储数据如果发生异常,需要进行回滚
		db.session.rollback()
		return jsonify(errno=RET.DBERR,errmsg='保存用户数据失败')
	# 返回用户信息到Redis数据库中
	session['user_id']=user.id
	session['mobile']=mobile
	session['nick_name']=mobile
	# 返回结果
	return jsonify(errno=RET.OK,errmsg='注册成功')

@passport_blue.route("/login",methods=['POST'])
def login():
	"""
	用户登录
	1、获取参数:mobile,password
	2、检查参数完整性
	3、检查手机号的格式
	4、根据手机号查询数据库,确认用户user存在
	5、调用模型类检查密码是否正确的方法
	6、记录用户的登录时间
	 user.last_login=datetime.now()
	7、提交数据库,如果发生异常需要回滚
	8、缓存用户信息session,昵称要换成user.nick_name
	8、返回结果
	:return:
	"""
	# 获取参数
	mobile=request.json.get('mobile')
	password=request.json.get('password')

	# 检查参数的完整性
	if not all([mobile,password]):
		return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
	# 检查手机号格式
	if not re.match(r'1[3456789]\d{9}$',mobile):
		return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')

	# 根据手机号查询数据库,确认用户已注册.
	try:
		user=User.query.filter_by(mobile=mobile).first()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')

	# 判断用户是否注册,以及密码是否正确.
	if user is None or not user.check_password(password):
		return jsonify(errno=RET.DATAERR,errmsg='用户名或密码错误')
	# 记录用户的登录时间
	user.last_login=datetime.now()
	# 提交数据到数据库中
	try:
		db.session.add(user)
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(errno=RET.DBERR,errmsg='保存数据失败')

	# 缓存用户信息到redis数据库中
	session['user_id']=user.id
	session['mobile']=mobile
	# 缓存的用户昵称和注册时要有区别,因为登录可以登录多次,昵称有可能会修改
	session['nick_name']=user.nick_name
	# 返回结果
	return jsonify(errno=RET.OK,errmsg='ok')


@passport_blue.route("/logout")
def logout():
	"""
	如果是前后端分离,以及符合RESTful风格,(表现层状态转换),退出的请求方法为delete
	get/post/put/delete 获取/新建/修改/删除
	退出登录
	1、本质是清除服务器缓存的用户信息
	:return:
	"""
	session.pop('user_id',None)
	session.pop('mobile',None)
	session.pop('nick_name',None)
	return jsonify(errno=RET.OK,errmsg='OK')
	pass


























































