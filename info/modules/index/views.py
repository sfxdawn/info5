from flask import session, render_template, current_app, jsonify

from info import constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blue
from werkzeug.routing import BaseConverter

@index_blue.route('/')
def index():
    """
    项目首页:
        用户数据展示
        1、使用session尝试从redis数据库中获取user_id
        2、如果user_id存在,根据id 查询mysql 数据库
        3、如果用户存在,如何返回头像和昵称
        user_info=user.to_dict()

        点击排行:
        1、业务处理,查询数据库
        2、按照点击次数排序    news_list=News.query.order_by(News.clicks.desc()).limit(6)
        3、遍历新闻列表,调用模型类中的to_dict() 函数



    :return:
    """
    # 尝试从redis中获取用户id
    user_id=session.get('user_id')
    # 如果user_id存在 查询数据库
    user=None
    if user_id:
        try:
            user=User.query.filter_by(id=user_id).first()
        except Exception as e:
            current_app.logger.error(e)

    #  点击排行---------------------------------------------------------------------
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻点击排行失败')

    # 判断查询结果是否为空
    if not news_list:
        return jsonify(errno=RET.NODATA,errmsg='无新闻数据')

    # 遍历新闻列表
    news_dict_list=[]
    for news in news_list:
        # 往临时的列表容器中添加新闻数据,to_dict调用了模型类中的方法,获取的是模型类中的指定数据
        news_dict_list.append(news.to_dict())


    #  首页新闻分类------------------------------------------------------------------------
    try:
        categories=Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询分类数据失败')
    # 判断查询结果是否存在
    if not categories:
        return jsonify(errno=RET.NODATA,errmsg='无分类数据')
    # 遍历查询结果
    category_list=[]
    for category in categories:
        category_list.append(category.to_dict())

    # 定义字典,用来存储返回项目首页的数据
    data={
        "user_info":user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "category_list": category_list,

    }

    return render_template('news/index.html',data=data)

@index_blue.route('/favicon.ico')
def favicon():
    # 项目title标签中的logo图标
    # 浏览器会访问项目根目录下的favicon.ico 文件 http://127.0.0.1:5000/static/news/favicon.ico
    # send_static_file 函数的作用是把static文件夹下的文件发给浏览器
    return current_app.send_static_file('/news/favicon.ico')







































