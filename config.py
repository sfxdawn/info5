from redis import StrictRedis

class Config:
    DEBUG = None
    SECRET_KEY='QR8WWud20L0G46OImCT/lzYvEHlO8P9++/G3ujEOKE1KIVjqtPRm1SP+Z3omFtUB'
    # 配置数据库的连接
    SQLALCHEMY_DATABASE_URI='mysql://root:Mysql@123@localhost/python5'
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    REDIS_HOST='127.0.0.1'
    REDIS_PORT='6379'
    # 状态保持的session信息要存储在redis数据库中
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True
    PERMANENT_SESSION_LIFETIME=86400


# 开发模式下的配置
class developmentConfig(Config):
    DEBUG=True
# 生产模式下的配置
class productionConfig(Config):
    DEBUG=False

# 定义字典,映射不同的配置类
config={
    'development':developmentConfig,
    'production':productionConfig
}