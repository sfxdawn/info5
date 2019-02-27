from redis import StrictRedis


class Config:
    DEBUG = True
    SECRET_KEY='QR8WWud20L0G46OImCT/lzYvEHlO8P9++/G3ujEOKE1KIVjqtPRm1SP+Z3omFtUB'

    # 状态保持的session信息要存储在redis数据库中
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host='127.0.0.1',port=6379)
    SESSION_USE_SIGNER=True
    PERMANENT_SESSION_LIFETIME=86400

