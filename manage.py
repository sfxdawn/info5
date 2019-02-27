from info import create_app,db,models
from flask import session
from flask_script import Manager


# 导入数据库迁移的扩展
from flask_migrate import Migrate,MigrateCommand

app=create_app('development')

manager=Manager(app)

Migrate(app,db)

# 使用迁移框架
manager.add_command('db',MigrateCommand)

@app.route('/')
def index():
    session['name']='2018'
    return 'hello world'

if __name__ == '__main__':
    manager.run()
