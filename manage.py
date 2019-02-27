from info import create_app
from flask import session
from flask_script import Manager

app=create_app('development')

manager=Manager(app)

@app.route('/')
def index():
    session['name']='2018'
    return 'hello world'

if __name__ == '__main__':
    manager.run()
