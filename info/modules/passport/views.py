from flask import request, jsonify, current_app, make_response
from random import random
from info.libs.yuntongxun import sms
from . import passport_blue
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store,constants
# 导入模型类
from info.models import User
import re
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
		if user is None:
			return jsonify(errno=RET.DATAEXIST,errmsg='用户已存在')
	#生成6位数短信随机数,使用随机数模块
	sms_code='%06d' % random.randint (0, 999999)
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









