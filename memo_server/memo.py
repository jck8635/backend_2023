from http import HTTPStatus
import random
import requests
import json
import urllib

from flask import abort, Flask, make_response, render_template, Response, redirect, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB 연결 설정
app.config['MONGO_URI'] = 'mongodb://localhost:27017/memos'  # 몽고DB URI
mongo = PyMongo(app)

# 메모 목록을 저장할 MongoDB 컬렉션
memos_collection = mongo.db.memos

naver_client_id = 'M6tACxPK5sQeF3K6e4k5'
naver_client_secret = 'bZvhwAYHEO'
naver_redirect_uri = 'http://localhost:8000/auth'
''''
  본인 app 의 것으로 교체할 것.
  여기 지정된 url 이 http://localhost:8000/auth 처럼 /auth 인 경우
  아래 onOAuthAuthorizationCodeRedirected() 에 @app.route('/auth') 태깅한 것처럼 해야 함
'''


@app.route('/')
def home():
    # 쿠기를 통해 이전에 로그인 한 적이 있는지를 확인한다.
    # 이 부분이 동작하기 위해서는 OAuth 에서 access token 을 얻어낸 뒤
    # user profile REST api 를 통해 유저 정보를 얻어낸 뒤 'userId' 라는 cookie 를 지정해야 된다.
    # (참고: 아래 onOAuthAuthorizationCodeRedirected() 마지막 부분 response.set_cookie('userId', user_id) 참고)
    userId = request.cookies.get('userId', default=None)
    name = None

    ####################################################
    # TODO: 아래 부분을 채워 넣으시오.
    #       userId 로부터 DB 에서 사용자 이름을 얻어오는 코드를 여기에 작성해야 함
    if userId:
        user_data = memos_collection.find_one({"userId": userId}, {"_id": 0, "name": 1})
        if user_data:
            name = user_data.get("name")

    ####################################################


    # 이제 클라에게 전송해 줄 index.html 을 생성한다.
    # template 로부터 받아와서 name 변수 값만 교체해준다.
    return render_template('index.html', name=name)


# 로그인 버튼을 누른 경우 이 API 를 호출한다.
# OAuth flow 상 브라우저에서 해당 URL 을 바로 호출할 수도 있으나,
# 브라우저가 CORS (Cross-origin Resource Sharing) 제약 때문에 HTML 을 받아온 서버가 아닌 곳에
# HTTP request 를 보낼 수 없는 경우가 있다. (예: 크롬 브라우저)
# 이를 우회하기 위해서 브라우저가 호출할 URL 을 HTML 에 하드코딩하지 않고,
# 아래처럼 서버가 주는 URL 로 redirect 하는 것으로 처리한다.
#
# 주의! 아래 API 는 잘 동작하기 때문에 손대지 말 것
@app.route('/login')
def onLogin():
    params={
            'response_type': 'code',
            'client_id': naver_client_id,
            'redirect_uri': naver_redirect_uri,
            'state': random.randint(0, 10000)
        }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/authorize?{urlencoded}'
    return redirect(url)


# 아래는 Redirect URI 로 등록된 경우 호출된다.
# 만일 본인의 Redirect URI 가 http://localhost:8000/auth 의 경우처럼 /auth 대신 다른 것을
# 사용한다면 아래 @app.route('/auth') 의 내용을 그 URL 로 바꿀 것
@app.route('/auth')
def onOAuthAuthorizationCodeRedirected():
    # TODO: 아래 1 ~ 4 를 채워 넣으시오.

    # 1. redirect uri 를 호출한 request 로부터 authorization code 와 state 정보를 얻어낸다.
    authorization_code = request.args.get('code')
    state = request.args.get('state')

    # 2. authorization code 로부터 access token 을 얻어내는 네이버 API 를 호출한다.
    naver_token_url = 'https://nid.naver.com/oauth2.0/token'
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': naver_client_id,
        'client_secret': naver_client_secret,
        'code': authorization_code,
        'state': state,
    }
    response = requests.post(naver_token_url, params=token_params)
    access_token = response.json().get('access_token')


    # 3. 얻어낸 access token 을 이용해서 프로필 정보를 반환하는 API 를 호출하고,
    #    유저의 고유 식별 번호를 얻어낸다.
    naver_profile_url = 'https://openapi.naver.com/v1/nid/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    profile_response = requests.get(naver_profile_url, headers=headers)
    profile_data = profile_response.json()
    

    # 4. 얻어낸 user id 와 name 을 DB 에 저장한다.
    user_id = profile_data.get('response', {}).get('id')
    user_name = profile_data.get('response', {}).get('name')


    # 5. 첫 페이지로 redirect 하는데 로그인 쿠키를 설정하고 보내준다.
    response = redirect('/')
    response.set_cookie('userId', user_id)

    return response


@app.route('/memo', methods=['GET'])
def get_memos():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # TODO: DB 에서 해당 userId 의 메모들을 읽어오도록 아래를 수정한다.
    ####################################################
    # TODO: 여기에 실제로 DB에서 메모를 읽어오는 코드를 추가하시오.
    #       result 에 DB에서 읽어온 메모 목록을 할당해야 함

    memos = memos_collection.find({'user_id': userId})
    result = [{'text': memo['text']} for memo in memos]

    ####################################################
    # memos라는 키 값으로 메모 목록 보내주기
    return ({'memos': result})


@app.route('/memo', methods=['POST'])
def post_new_memo():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # 클라이언트로부터 JSON 을 받았어야 한다.
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)

    # TODO: 클라이언트로부터 받은 JSON 에서 메모 내용을 추출한 후 DB에 userId 의 메모로 추가한다.
    data = request.get_json()
    text = data.get('text', '')

    # MongoDB에 새 메모 추가
    new_memo = {'user_id': userId, 'text': text}
    memos_collection.insert_one(new_memo)

    #
    return '', HTTPStatus.OK


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)