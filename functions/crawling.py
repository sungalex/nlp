'''
crawling 모듈은 웹사이트의 Iinternal Link와 External Link를 순회하며 URL 정보를
수집하는 함수들을 포함하고 있습니다.
'''

from bs4 import BeautifulSoup
from functions.download import getDownload
from urllib.parse import urljoin


def getUrls(link, depth=3):
    '''
    link 사이트를 다운로드 받은 후 html에 포함된 url를 추출하여, url과 depth를
    dictionary list를 반환 합니다.

    internalLink와 externalLink로 구분 후 internalLink는 scheme과 netloc를
    추가혀 절대 주소로 바꾼 후 dictionary에 추가한다. 

    link: 탐색할 url
    depth: 탐색할 url이 처음 시작한 url로 부터 몇번째 depth인지 나타내며, 3보다
    크면 탐색을 종료함
    '''
    if depth > 3:    # getUrls() 호출은 depth를 3단계 까지만 수행하도록 제한
        return None

    links = []

    html = getDownload(link)
    dom = BeautifulSoup(html.text, "lxml")

    for a in dom.select("a"):
        if a.has_attr("href"):
            if a["href"].startswith("http"):    # externalLink : HTTP(S)
                links.append({"url": a["href"], "depth": depth + 1})
            elif a["href"].startswith("/"):    # internalLink : /
                href = urljoin(link, a["href"])
                links.append({"url": href, "depth": depth + 1})
            else:
                # print("Skipped: {0}".format(a["href"]))
                pass

    print("{0} {1} --> {2}개 사이트 추가".format(">" * (depth + 1), link, len(links)))

    return links
