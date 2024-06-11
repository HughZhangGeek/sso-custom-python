# coding=utf-8
from datetime import datetime, timedelta
from flask import Flask, abort, redirect, request
import jwt


class Const:
    ACS = 'https://www.jiandaoyun.com/sso/custom/6062f528353e650007292c5a/acs'
    SECRET = 'test'
    ISSUER = 'com.example'
    USERNAME = 'zhangsan'
    LOGOUT_URL = 'https://www.jiandaoyun.com'  # 用户访问登出地址进行登出或点击退出按钮进行登出时，均会跳转到此页面


app = Flask(__name__)


def valid_token(query):
    try:
        token = jwt.decode(
            query, Const.SECRET,
            audience=Const.ISSUER,
            issuer='com.jiandaoyun'
        )
        return token.get('type') == 'sso_req'
    except InvalidTokenError:
        return False


def get_token_from_username(username):
    now = datetime.utcnow()
    return jwt.encode({
        "type": "sso_res",
        'username': username,
        'iss': Const.ISSUER,
        "aud": "com.jiandaoyun",
        "nbf": now,
        "iat": now,
        "exp": now + timedelta(seconds=60),
        "jti": "for_test"  # 任意字符串
    }, Const.SECRET, algorithm='HS256').decode('utf-8')


@app.route('/sso', methods=['GET'])
def handler():
    query = request.args.get('request', default='')
    state = request.args.get('state')
    if valid_token(query):
        token = get_token_from_username(Const.USERNAME)
        stateQuery = "" if not state else f"&state={state}"
        return redirect(f'{Const.ACS}?response={token}{stateQuery}')
    else:
        return abort(404)


# IdP 登出接口重定向
@app.route('/logout', methods=['GET'])
def logout():
    return redirect(Const.LOGOUT_URL)


if __name__ == '__main__':
    app.run(port=8080)
