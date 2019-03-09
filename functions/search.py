# search 모듈은 download 모듈을 이용하여 포탈 사이트의 검색결과 중 특정
# 데이터를 추출하는 함수들을 포함하고 있다.

import requests
from functions.download import getDownload
from functions.download import postDownload
from functions.download import putSubmit
from bs4 import BeautifulSoup

def googleSearchSubject(searchString=None):
    '''
    이 함수는 구글에서 지정한 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    searchString : 검색할 문자열(String)
    '''
    url = "http://www.google.com/search"
    html = getDownload(url, params={"q":searchString})

    dom = BeautifulSoup(html.text, "lxml")
    tags = dom.find_all("div", {"class":"r"})

    result = []

    for tag in tags:
        result.append(tag.find("a").h3.text)

    return result

def naverSearchSubject(searchString=None):
    '''
    이 함수는 네이버에서 지정한 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    searchString : 검색할 문자열(String)

    return 값은 섹션별로 제목 리스트를 포함하고 있는 List(2차원 배열) 입니다.
    '''
    url = "https://search.naver.com/search.naver"

    html = getDownload(url, params={"query": searchString})
    dom = BeautifulSoup(html.text, "lxml")
    ulTags = dom.find_all("", {"class":"type01"})

    result = []

    for ul in ulTags:
        section = []
        for dt in ul.find_all("dt"):
            section.append(dt.a.text)
        result.append(section)

    return result

def daumSearchSubject():
    pass

def googleSearchUrl():
    pass

def naverSearchUrl():
    pass

def daumSearchUrl():
    pass
