'''
search 모듈은 download 모듈을 이용하여 포탈 사이트의 검색결과 중 특정
데이터를 추출하는 함수들을 포함하고 있습니다.
'''

import requests
from functions.download import getDownload
from functions.download import postDownload
from functions.download import putSubmit
from bs4 import BeautifulSoup


def googleSearchTitleList(searchString=None):
    '''
    이 함수는 구글에서 지정한 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    google 검색결과를 분석해보면, 제목 바로 위에 있는 div 태그의 class명이 "r"로
    일정한 것을 발견할 수 있습니다. <h3 class="r"> 태그 하부에 <a> 태그의 text
    부분에 제목이 보입니다. <a> 태그의 text에는 제목과 URL이 함께 표시되기
    때문에 제목 만 가져오기 위해서는 <a> 태그 내에 있는 <h3> 태그의 text 만을
    가져오면 됩니다.

    searchString : 검색할 문자열(String)
    '''
    url = "http://www.google.com/search"
    html = getDownload(url, params={"q": searchString})

    dom = BeautifulSoup(html.text, "lxml")
    tags = dom.find_all("div", {"class": "r"})

    result = []

    for tag in tags:
        result.append(tag.find("a").h3.text)

    return result


def naverSearchTitleList(searchString=None):
    '''
    이 함수는 네이버에서 지정한 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    naver 검색결과는 class명이 "main_pack"인 <div> 태그 하부에 존재 합니다.
    검색결과 우측의 뉴스토픽은 class명이 "sub_pack"인 <div> 태그 내에 존재
    합니다. 검색결과는 블로그, 카페, 동영상, 뉴스, 지식인, 웹사이트, 이미지
    섹션으로 구분되어 있고, 동영상, 이미지 섹션을 제외하고는 공통적으로 <ul>
    태그의 class명이 "type01" 이고, <ul> 태그 아래 <li> 태그 내에 세부 리스트가
    있습니다. 블로그 만 검색하려면 class명 "sh_blog_top"를, 카페 만 검색하려면
    class명 "sh_cafe_top"를 사용할 수 있습니다. 검색결과 리스트의 제목은 <ul>
    - <li> - <dl> - <dt> - <a> 태그 구조로 되어 있고, <a> 태그의 text가
    제목 문자열 입니다. "type01" class를 찾은 후, <dt> 태그 내에 있는 <a>
    태그의 text를 찾으면 됩니다.(<a> 태그를 바로 찾으면 불필요한 내용이
    포함됩니다.)

    searchString : 검색할 문자열(String)

    return 값은 섹션별로 제목 리스트를 포함하고 있는 List(2차원 배열) 입니다.
    '''
    url = "https://search.naver.com/search.naver"

    html = getDownload(url, params={"query": searchString})
    dom = BeautifulSoup(html.text, "lxml")
    ulTags = dom.find_all("", {"class": "type01"})

    result = []

    for ul in ulTags:
        section = []
        for dt in ul.find_all("dt"):
            section.append(dt.a.text)
        result.append(section)

    return result


def daumSearchTitleList(searchString):
    '''
    이 함수는 다음 포탈에서 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    Daum 검색결과는 class이 "inner_article"인 <div> 태그 하부에 존재 합니다.
    검색결과는 블로그, 웹문서, 브런치, 이미지, 뉴스, 카페글 섹션으로 구분되어
    있고, 다행이 각 섹션의 <div> 태그의 class명이 "g_comp"로 동일 합니다. 세부
    검색 리스트는 "g_comp" class 하부에 포함된 <ul> 태그 아래 <li> 태그들
    아래에 존재합니다. 찾고자 하는 제목은 <li> 태그 아래에 <a> 태그에 있지만,
    <a> 태그까지 찾아가는 경로는 섹션마다 조금씩 다르고, <li> 태그 내에는
    불필요한 <a> 태그도 존재합니다. 블로그, 웹문서, 뉴스, 카페글 섹션은 제목을
    나타내는 <a> 태그의 바로 위 <div> 태그의 class명이 "mg_tit"로 동일 합니다.
    "mg_tit" class명을 이용해서 블로그, 웹문서, 뉴스, 카페글에서 제목을
    추출합니다.

    searchString: 검색할 문자열(String)
    '''
    url = "https://search.daum.net/search"

    html = getDownload(url, params={"q": searchString})
    dom = BeautifulSoup(html.text, "lxml")
    divTags = dom.find_all("", {"class": "mg_tit"})

    result = []

    for tag in divTags:
        result.append(tag.find("a").text.strip())

    return result


def getSearchTitleList(portal="google", searchString=None):
    '''
    지정한 검색 포탈에서 지정한 문자열을 찾은 후 검색결과 중 제목 List를 Return
    합니다.

    portal: "google", "g", "naver", "n", "daum", "d" 중 하나를 지정(default는 "google")
    searchString: 검색할 문자열(String)
    '''
    portal = portal.lower()

    if portal in ["google", "g"]:
        resp = googleSearchTitleList(searchString)
    elif portal in ["naver", "n"]:
        resp = naverSearchTitleList(searchString)
    elif portal in ["daum", "d"]:
        resp = daumSearchTitleList(searchString)
    else:
        resp = []
        print('portal은 "google", "g", "naver", "n", "daum", "d" 중 하나를 지정하세요.')

    return resp

def googleSearchUrlList():
    pass


def naverSearchUrlList():
    pass


def daumSearchUrlList():
    pass
