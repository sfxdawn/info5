from flask import Flask

app=Flask(__name__)

app.config.from_pyfile("config.ini")

@app.route('/')
def index():
    return 'hello world'

@app.route("/abc")
def abc():
    return "abc的页面"

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8888)



#
#
#
# class  Config(object):
#     DEBUG=True
#
#
# # 创建Flask 类的对象，指向程序所在的包的名称
# app=Flask(__name__)
#
# # 从配置对象中加载配置
# app.config.from_object(Config)
#
#
# # 使用代码去加载配置
# # 打一个包裹
# app=Flask(__name__)
#
# # 从配置文件中加载配置
# app.config.from_pyfile('config.ini')
#
#
#
# # 使用代码去加载配置：
# # 打一个包裹
# app=Flask(__name__)
# # 加载指定环境变量名称所对应的相关配置
# app.config.from_envvar('FLASKCONFIG')
#
#
#
# # 读取配置：
# app.config.get()
# # 在视图函数中使用current_app.config.get()

"""
注意： Flask 应用程序将一些常用的配置设置成了应用程序对象属性，也可以通过属性直接设置、获取某些配置：app.debug= True 

app.run的参数
可以指定运行的主机IP 地址，端口，是否开启调试模式
app.run(host="0.0.0.0",port=5000,debug= True)

"""





























