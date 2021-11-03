from flask import Flask
import json

from flask_blueprint.yuehou import yuehou

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.register_blueprint(yuehou, url_prefix='/yuehou')


@app.errorhandler(400)
def page_not_found(error):
    # 客户端语法错误
    return json.dumps({'code': 400}), 400


@app.errorhandler(405)
def page_not_found(error):
    # 客户端请求中的方法被禁止
    return json.dumps({'code': 405}), 405
