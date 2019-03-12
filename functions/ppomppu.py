'''
뽐뿌(http://www.ppomppu.co.kr) 사이트의 뽐뿌게시판과 자유게시판 정보를 추출하기 위한
함수들을 포함하고 있습니다.
'''

from bs4 import BeautifulSoup
from functions.download import getDownload
from urllib.parse import urljoin
from datetime import datetime
import os
import sys

url = "http://www.ppomppu.co.kr/zboard/zboard.php"


class Ppomppu():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 뽐뿌게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self):
        self.param = {"id": "ppomppu"}
        self.html = getDownload(url, self.param)
        self.bs = BeautifulSoup(self.html.text, "html.parser")

    def getNumber(self):
        pass

    def getCategory(self):
        pass

    def getWriter(self):
        pass

    def getTitle(self):
        title = []
        for tag in self.bs.select("table font.list_title"):
            title.append(tag.text.strip())
        return title

    def getLink(self):
        link = []
        for tag in self.bs.select("table font.list_title"):
            link.append(urljoin(url, tag.find_parent()["href"]))
        return link

    def getImageSource(self):
        imgList = []

        for tag in self.bs.select("table img.thumb_border"):
            imgList.append(urljoin(url, tag["src"]))

        return imgList

    def downloadImage(self):
        imgList = self.getImageSource()

        now = datetime.now().isoformat()
        day_hour_minute = now[:10] + "_" + now[11:13] + "-" + now[14:16]
        path = "images/ppompu/" + day_hour_minute
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            raise os.OSError(
                "(%s) 디렉토리를 만들 수 없습니다!" % (path))

        fileList = []

        for src in imgList:
            img = getDownload(src)
            imgName = src.split("/")[-1].split("?")[0]

            fileName = path + "/" + imgName

            with open(fileName, "wb") as f:
                f.write(img.content)
                fileList.append(fileName)

        return fileList

    def getReplyCount(self):
        pass

    def getWriteDate(self):
        pass

    def getLikeCount(self):
        pass

    def getQueryCount(self):
        pass

    def getReplyContent(self):
        pass

    def getComments(self):
        pass

    def getPpomppuList(self):
        pass


class PpomppuFreeboard():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 자유게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self):
        self.param = {"id": "freeboard"}
        self.html = getDownload(url, self.param)
        self.bs = BeautifulSoup(self.html.text, "html.parser")

    def getNumber(self):
        pass

    def getCategory(self):
        pass

    def getWriter(self):
        pass

    def getTitle(self):
        pass

    def getUrl(self):
        pass

    def getImage(self):
        pass

    def getReplyCount(self):
        pass

    def getWriteDate(self):
        pass

    def getLikeCount(self):
        pass

    def getQueryCount(self):
        pass

    def getReplyContent(self):
        pass

    def getComments(self):
        pass

    def getFreeboardList(self):
        pass
