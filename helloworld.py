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














