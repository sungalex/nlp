'''
search 모듈은 download 모듈을 이용하여 포탈 사이트의 검색결과 중 특정
데이터를 추출하는 함수들을 포함하고 있습니다.
'''

import requests
from functions.download import get_download
from bs4 import BeautifulSoup

google_url = "http://www.google.com/search"
naver_url = "https://search.naver.com/search.naver"
daum_url = "https://search.daum.net/search"
nate_url = "https://search.daum.net/nate"


def get_google_title(search_string=None):
    '''
    이 함수는 구글에서 지정한 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다.

    google 검색결과를 분석해보면, 제목 바로 위에 있는 div 태그의 class명이 "r"로
    일정한 것을 발견할 수 있습니다. <h3 class="r"> 태그 하부에 <a> 태그의 text
    부분에 제목이 보입니다. <a> 태그의 text에는 제목과 URL이 함께 표시되기
    때문에 제목 만 가져오기 위해서는 <a> 태그 내에 있는 <h3> 태그의 text 만을
    가져오면 됩니다.

    search_string : 검색할 문자열(String)
    '''
    html = get_download(google_url, params={"q": search_string})

    dom = BeautifulSoup(html.text, "lxml")
    tags = dom.find_all("div", {"class": "r"})

    result = []

    for tag in tags:
        result.append(tag.find("a").h3.text.strip())

    return result


def get_naver_title(search_string=None):
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

    search_string : 검색할 문자열(String)

    return 값은 섹션별로 제목 리스트를 포함하고 있는 List(2차원 배열) 입니다.
    '''
    html = get_download(naver_url, params={"query": search_string})
    dom = BeautifulSoup(html.text, "lxml")
    ulTags = dom.find_all("", {"class": "type01"})

    result = []

    for ul in ulTags:
        section = []
        for dt in ul.find_all("dt"):
            section.append(dt.a.text.strip())
        result.append(section)

    return result


def get_daum_title(search_string=None):
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

    search_string: 검색할 문자열(String)
    '''
    html = get_download(daum_url, params={"q": search_string})
    dom = BeautifulSoup(html.text, "lxml")
    divTags = dom.find_all("", {"class": "mg_tit"})

    result = []

    for tag in divTags:
        a = tag.find("a")
        if a != None:
            result.append(a.text.strip())
    return result


def get_nate_title(search_string=None):
    '''
    이 함수는 네이트 포탈에서 문자열을 검색 후 검색결과 중 제목 List를 Return
    합니다. (편의상 블로그 검색 결과만 Return 합니다.)

    네이트는 다음 검색을 이용합니다. 
    
    블로그 검색 결과는 id가 "blogColl"인 <div> 태그 하부에 존재 합니다.
    <a> 태그의 class명 "f_link_b" 내에 제목이 있습니다.

    search_string: 검색할 문자열(String)
    '''
    html = get_download(nate_url, params={"q": search_string})
    dom = BeautifulSoup(html.text, "lxml")

    result = []

    blog = dom.find("", {"id":"blogColl"})
    for tag in blog.find_all("a", {"class":"f_link_b"}):
        result.append(tag.text)

    return result


def get_portal_title(portal="google", search_string=None):
    '''
    지정한 검색 포탈에서 지정한 문자열을 찾은 후 검색결과 중 제목 List를 Return
    합니다.

    portal: "google", "g", "naver", "n", "daum", "d", "nate", "na" 중 하나를 지정(default는 "google")
    search_string: 검색할 문자열(String)
    '''
    portal = portal.lower()

    if portal in ["google", "g"]:
        resp = get_google_title(search_string)
    elif portal in ["naver", "n"]:
        resp = get_naver_title(search_string)
    elif portal in ["daum", "d"]:
        resp = get_daum_title(search_string)
    elif portal in ["nate", "na"]:
        resp = get_nate_title(search_string)
    else:
        resp = []
        print('portal은 "google", "g", "naver", "n", "daum", "d", "nate", "na" 중 하나를 지정하세요.')

    return resp


def get_google_title_with_url(search_string=None):
    '''
    이 함수는 구글에서 지정한 문자열을 검색 후 검색결과 중 제목과 URL List를 Return
    합니다.

    google 검색결과를 분석해보면, 제목 바로 위에 있는 div 태그의 class명이 "r"로
    일정한 것을 발견할 수 있습니다. <h3 class="r"> 태그 하부에 <a> 태그의 text
    부분에 제목이 보입니다. <a> 태그의 text에는 제목과 URL이 함께 표시되기
    때문에 제목 만 가져오기 위해서는 <a> 태그 내에 있는 <h3> 태그의 text 만을
    가져오면 됩니다.

    URL은 <a> 태그 내에 있는 "href" 속성을 가져오면 됩니다. 

    search_string : 검색할 문자열(String)
    '''
    html = get_download(google_url, params={"q": search_string})

    dom = BeautifulSoup(html.text, "lxml")
    tags = dom.find_all("div", {"class": "r"})

    result = []

    for tag in tags:
        title = tag.find("a").h3.text.strip()
        url = tag.find("a").get("href")
        result.append([title, url])

    return result


def get_naver_title_with_url(search_string=None):
    '''
    이 함수는 네이버에서 지정한 문자열을 검색 후 검색결과 중 제목과 URL List를 Return
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

    URL은 <a> 태그 내에 있는 "href" 속성을 가져오면 됩니다. 

    search_string : 검색할 문자열(String)

    return 값은 섹션별로 제목 리스트를 포함하고 있는 List(2차원 배열) 입니다.
    '''
    html = get_download(naver_url, params={"query": search_string})
    dom = BeautifulSoup(html.text, "lxml")
    ulTags = dom.find_all("", {"class": "type01"})

    result = []

    for ul in ulTags:
        section = []
        for dt in ul.find_all("dt"):
            title = dt.a.text.strip()
            url = dt.a.get("href")
            section.append([title, url])
        result.append(section)

    return result


def get_daum_title_with_url(search_string=None):
    '''
    이 함수는 다음 포탈에서 문자열을 검색 후 검색결과 중 제목과 URL List를 Return
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

    URL은 <a> 태그 내에 있는 "href" 속성을 가져오면 됩니다. 

    search_string: 검색할 문자열(String)
    '''
    html = get_download(daum_url, params={"q": search_string})
    dom = BeautifulSoup(html.text, "lxml")
    divTags = dom.find_all("", {"class": "mg_tit"})

    result = []

    for tag in divTags:
        a = tag.find("a")
        if a != None:
            title = a.text.strip()
            url = a.get("href")
            result.append([title, url])

    return result


def get_nate_title_with_url(search_string=None):
    '''
    이 함수는 네이트 포탈에서 문자열을 검색 후 검색결과 중 제목과 URL List를 Return
    합니다.
    (편의상 블로그 검색 결과만 Return 합니다.)

    URL은 <a> 태그 내에 있는 "href" 속성을 가져오면 됩니다. 

    search_string: 검색할 문자열(String)
    '''
    html = get_download(nate_url, params={"q": search_string})
    dom = BeautifulSoup(html.text, "lxml")

    result = []

    blog = dom.find("", {"id":"blogColl"})
    for tag in blog.find_all("a", {"class":"f_link_b"}):
        title = tag.text.strip()
        url = tag["href"]
        result.append([title, url])

    return result


def get_portal_title_with_url(portal="google", search_string=None):
    '''
    지정한 검색 포탈에서 지정한 문자열을 찾은 후 검색결과 중 제목과 URL List를 Return
    합니다.

    portal: "google", "g", "naver", "n", "daum", "d" 중 하나를 지정(default는 "google")
    search_string: 검색할 문자열(String)
    '''
    portal = portal.lower()

    if portal in ["google", "g"]:
        resp = get_google_title_with_url(search_string)
    elif portal in ["naver", "n"]:
        resp = get_naver_title_with_url(search_string)
    elif portal in ["daum", "d"]:
        resp = get_daum_title_with_url(search_string)
    elif portal in ["nate", "na"]:
        resp = get_nate_title_with_url(search_string)
    else:
        resp = []
        print('portal은 "google", "g", "naver", "n", "daum", "d", "nate", "na" 중 하나를 지정하세요.')

    return resp


def get_portal_to_dom(search_string=None):
    '''
    구글, 네이버, 다음 포탈에서 특정 문자열을 검색한 결과를 DOM 객체 List로 반환
    합니다.

    portal: "google", "g", "naver", "n", "daum", "d" 중 하나를 지정(default는 "google")
    search_string: 검색할 문자열(String)
    '''
    google_html = get_download(google_url, params={"q": search_string})
    naver_html = get_download(naver_url, params={"query": search_string})
    daum_html = get_download(daum_url, params={"q": search_string})
    nate_html = get_download(nate_url, params={"q": search_string})

    google_dom = BeautifulSoup(google_html.text, "lxml")
    naver_dom = BeautifulSoup(naver_html.text, "lxml")
    daum_dom = BeautifulSoup(daum_html.text, "lxml")
    nate_dom = BeautifulSoup(nate_html.text, "lxml")

    return (google_dom, naver_dom, daum_dom, nate_dom)


def get_portal_search_url():
    return (google_url, naver_url, daum_url, nate_url)


def getGoogleTitle(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_google_title()로 변경 되었습니다.
    '''
    return get_google_title(searchString)

def getNaverTitle(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_naver_title()로 변경 되었습니다.
    '''
    return get_naver_title(searchString)

def getDaumTitle(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_daum_title()로 변경 되었습니다.
    '''
    return get_daum_title(searchString)

def getNateTitle(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_nate_title()로 변경 되었습니다.
    '''
    return get_nate_title(searchString)

def getPortalTitle(portal="google", searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_portal_title()로 변경 되었습니다.
    '''
    return get_portal_title(portal, searchString)

def getGoogleTitleWithUrl(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_google_title_with_url()로 변경 되었습니다.
    '''
    return get_google_title_with_url(searchString)

def getNaverTitleWithUrl(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_naver_title_with_url()로 변경 되었습니다.
    '''
    return get_naver_title_with_url(searchString)

def getDaumTitleWithUrl(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_daum_title_with_url()로 변경 되었습니다.
    '''
    return get_daum_title_with_url(searchString)

def getNateTitleWithUrl(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_nate_title_with_url()로 변경 되었습니다.
    '''
    return get_nate_title_with_url(searchString)

def getPortalTitleWithUrl(portal="google", searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_portal_title_with_url()로 변경 되었습니다.
    '''
    return get_portal_title_with_url(portal, searchString)

def getPortalToDOM(searchString=None):
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_portal_to_dom()로 변경 되었습니다.
    '''
    return get_portal_to_dom(searchString)

def getPortalSearchUrl():
    '''
    Deprecated: 함수명 규칙 변경에 따라 함수명이 get_portal_search_url()로 변경 되었습니다.
    '''
    return get_portal_search_url()
