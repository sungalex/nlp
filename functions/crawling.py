'''
crawling 모듈은 웹사이트의 Iinternal Link와 External Link를 순회하며 URL 정보를
수집하는 함수들을 포함하고 있습니다.

//To-Do: 함수들을 class 메서드로 재정의 필요
'''
import re
import datetime
import random

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from functions.download import get_download


pages = set()
allExtLinks = set()
allIntLinks = set()
random.seed(datetime.datetime.now())


def get_site_urls(link, depth=3):
    '''
    link 사이트를 다운로드 받은 후 html에 포함된 url를 추출하여, url과 depth를
    dictionary list를 반환 합니다.

    internalLink와 externalLink로 구분 후 internalLink는 scheme과 netloc를
    추가해 절대 주소로 바꾼 후 dictionary에 추가한다. 

    link: 탐색할 url
    depth: 탐색할 url이 처음 시작한 url로 부터 몇번째 depth인지 나타내며, 
    default는 3보다 크면 탐색을 종료함
    '''
    if depth > 3:    # get_url() 호출은 depth를 3단계 까지만 수행하도록 제한
        return None

    links = []

    html = get_download(link)
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


#Retrieves a list of all Internal links found on a page
def getInternalLinks(bsObj, includeUrl):
    includeUrl = urlparse(includeUrl).scheme+"://"+urlparse(includeUrl).netloc
    internalLinks = []
    #Finds all links that begin with a "/"
    for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                if(link.attrs['href'].startswith("/")):
                    internalLinks.append(includeUrl+link.attrs['href'])
                else:
                    internalLinks.append(link.attrs['href'])
    return internalLinks
            
#Retrieves a list of all external links found on a page
def getExternalLinks(bsObj, excludeUrl):
    externalLinks = []
    #Finds all links that start with "http" or "www" that do
    #not contain the current URL
    for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in externalLinks:
                externalLinks.append(link.attrs['href'])
    return externalLinks


def getRandomExternalLink(startingPage):
    html = urlopen(startingPage)
    bsObj = BeautifulSoup(html, "html.parser")
    externalLinks = getExternalLinks(bsObj, urlparse(startingPage).netloc)
    if len(externalLinks) == 0:
        print("No external links, looking around the site for one")
        domain = urlparse(startingPage).scheme+"://"+urlparse(startingPage).netloc
        internalLinks = getInternalLinks(bsObj, domain)
        return getRandomExternalLink(internalLinks[random.randint(0,len(internalLinks)-1)])
    else:
        return externalLinks[random.randint(0, len(externalLinks)-1)]
    
def followExternalOnly(startingSite):
    externalLink = getRandomExternalLink(startingSite)
    print("Random external link is: "+externalLink)
    followExternalOnly(externalLink)
            
#Collects a list of all external URLs found on the site
def getAllExternalLinks(siteUrl):
    html = urlopen(siteUrl)
    domain = urlparse(siteUrl).scheme+"://"+urlparse(siteUrl).netloc
    bsObj = BeautifulSoup(html, "html.parser")
    internalLinks = getInternalLinks(bsObj,domain)
    externalLinks = getExternalLinks(bsObj,domain)

    for link in externalLinks:
        if link not in allExtLinks:
            allExtLinks.add(link)
            print(link)
    for link in internalLinks:
        if link not in allIntLinks:
            allIntLinks.add(link)
            getAllExternalLinks(link)

# followExternalOnly("http://oreilly.com")
# 
# allIntLinks.add("http://oreilly.com")
# getAllExternalLinks("http://oreilly.com")