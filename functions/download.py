'''
download 모듈은 requests 패키지를 이용해 웹에서 컨텐츠를 다운로드 하는
함수들을 포함하고 있습니다.
'''

import requests
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
from requests.exceptions import RequestException

# header : 서버에 전달할 user-agent 정보(사용자 환경에 따라 달라짐)
header = {
    "user-agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) \
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
}

# base_retries : 서버 오류 시 접속 재시도 할 회수
base_retries = 3


# get Method 방식으로 웹 컨텐츠를 다운로드 하는 함수
def getDownload(url, params=None, headers=header, retries=base_retries):
    '''
    이 함수는 지정한 url에 get Method 방식으로 params의 Query String을
    전달하고 그 결과(Response)를 Return 합니다.

    url: 다운로드 할 웹 페이지 URL(String)
    params: 웹 페이지에 get Method 방식으로 전달할 Query String(Dictionary)
    headers: HTTP Request header 부분에 포함할 parameters(Dictionary)
    retries: 서버 에러 시 접속 재시도(getDownload 함수 재호출) 횟수(integer)
    '''
    resp = None

    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
    except HTTPError as e:
        if 500 <= resp.status_code < 600 and retries > 0:
            print("Retries: {0}".format(base_retries - retries + 1))
            return getDownload(url, params, headers, retries - 1)
        else:
            print("HTTPError:[{}]:{}, {}".format(resp.status_code, resp.reason,
                                                 resp.headers))
    except ConnectionError as e:
        print("ConnectionError:{}".format(e))
    except RequestException as e:
        print("UnexpectedError:{}".format(e))

    return resp


# post Method 방식으로 웹 컨텐츠를 다운로드 하는 함수
def postDownload(url,
                 data=None,
                 cookie=None,
                 headers=header,
                 retries=base_retries):
    '''
    이 함수는 지정한 url에 post Method 방식으로 data의 Submit Dictionary를
    전달하고 그 결과(Response)를 Return 합니다.

    url: post 메서드를 전달 할 웹 페이지 URL(String)
    data: 웹 페이지에 post Method 방식으로 전달할 submit data(Dictionary)
    cookie: 웹 페이지에 전달할 쿠기 정보(String)
    headers: HTTP Request header 부분에 포함할 parameters(Dictionary)
    retries: 서버 에러 시 접속 재시도(getDownload 함수 재호출) 횟수(integer)
    '''
    resp = None

    try:
        resp = requests.post(url, data=data, cookies=cookie, headers=headers)
        resp.raise_for_status()
    except HTTPError as e:
        if 500 <= resp.status_code < 600 and retries > 0:
            print("Retries: {0}".format(base_retries - retries + 1))
            return postDownload(url, data, cookie, headers, retries - 1)
        else:
            print("HTTPError:[{}]:{}, {}".format(resp.status_code, resp.reason,
                                                 resp.headers))
    except ConnectionError as e:
        print("ConnectionError:{}".format(e))
    except RequestException as e:
        print("UnexpectedError:{}".format(e))

    return resp


# put Method 방식으로 웹 컨텐츠를 수정하는 함수
def putSubmit(url, data=None, cookie=None, headers=header,
              retries=base_retries):
    '''
    이 함수는 지정한 url에 put Method 방식으로 data의 Submit Dictionary를
    전달해서 DB를 수정하고, 그 결과(Response)를 Return 합니다.

    url: put 메서드를 전달 할 웹 페이지 URL(String)
    data: 웹 페이지에 put Method 방식으로 전달할 submit data(Dictionary)
    cookie: 웹 페이지에 전달할 쿠기 정보(String)
    headers: HTTP Request header 부분에 포함할 parameters(Dictionary)
    retries: 서버 에러 시 접속 재시도(getDownload 함수 재호출) 횟수(integer)
    '''
    resp = None

    try:
        resp = requests.put(url, data=data, cookies=cookie, headers=headers)
        resp.raise_for_status()
    except HTTPError as e:
        if 500 <= resp.status_code < 600 and retries > 0:
            print("Retries: {0}".format(base_retries - retries + 1))
            return putDownload(url, data, cookie, headers, retries - 1)
        else:
            print("HTTPError:[{}]:{}, {}".format(resp.status_code, resp.reason,
                                                 resp.headers))
    except ConnectionError as e:
        print("ConnectionError:{}".format(e))
    except RequestException as e:
        print("UnexpectedError:{}".format(e))

    return resp
