from flask import session, render_template, current_app

from . import index_blue
from werkzeug.routing import BaseConverter




@index_blue.route('/')
def index():
    session['name']='2018'
    return render_template('news/index.html')

@index_blue.route('/favicon.ico')
def favicon():
    # 项目title标签中的logo图标
    # 浏览器会访问项目根目录下的favicon.ico 文件 http://127.0.0.1:5000/static/news/favicon.ico
    # send_static_file 函数的作用是把static文件夹下的文件发给浏览器
    return current_app.send_static_file('/news/favicon.ico')







































