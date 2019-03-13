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


class Ppomppu():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 뽐뿌게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self, category=None):
        '''
        Ppomppu 객체를 생성합니다.
        
        객체 생성 시 category 값을 전달하면, 해당 category 게시글만 List 됩니다.
        category를 지정하지 않으면 전체 게시글이 List 됩니다.
        
        category 값은 아래와 같습니다.
            1:기타
            4~6:컴퓨터,디니털,먹거리
            8~13:서적,가전/가구,육아,카메라,의류/잡화,화장품
            15:등산/캠핑
        '''
        self.url = "http://www.ppomppu.co.kr/zboard/zboard.php"
        self.param = {"id": "ppomppu", "category": category}
        self.html = getDownload(self.url, self.param)
        self.bs = BeautifulSoup(self.html.text, "html.parser")
        self.intStrings = self.getIntStrings()

    def getIntStrings(self):
        '''
        "td.eng.list_vspace" 클래스명으로 나타나는 integer String형 자료
        3개(3개 열)의 값을 반환 합니다.
        
        이 3개의 열을 구분할 만한 ID/Class 정보가 없기 때문에 한꺼번에 추출 후
        순서에 따하 해당 컬럼 자료로 분류해서 사용 합니다.
        첫번째 자료는 "번호", 두번째 자료는 "추천", 세번째 자료는 "조회수"를
        의미 합니다. getNumbers(), getLikeCounts(), getQueryCounts() 함수에서
        이 값을 사용합니다.

        이 함수는 객체 생성 시 호출됩니다.
        '''
        intStrings = []

        for tag in self.bs.select("tr > td.eng.list_vspace"):
            if not tag.has_attr("title"):
                intStrings.append(tag.text.strip())

        return intStrings

    def getNumbers(self):
        '''
        게시글 번호를 반환 합니다.
        '''
        numbers = []

        for intString in self.intStrings:
            if self.intStrings.index(intString) % 3 == 0:
                numbers.append(intString)

        return numbers

    def getCategorys(self):
        '''
        게시글 별 분류 카테고리를 반환 합니다.

        '''
        categorys = []

        for tag in self.bs.select("td.han4.list_vspace"):
            categorys.append(tag.text.strip())

        return categorys

    def getWriters(self):
        '''
        게시글 별 글쓴이 필명을 반환 합니다.
        '''
        writers = []

        for tag in self.bs.select("div.list_name"):
            if not tag.find_parent().find_parent()["class"][0] == "list_notice":
                writer = tag.find("a").text.strip()
                if len(writer) == 0:
                    if tag.find("img").has_attr("alt"):
                        writers.append(tag.find("img")["alt"])
                    else:
                        writers.append(None)
                else:
                    writers.append(writer)

        return writers

    def getTitles(self):
        '''
        게시글 별 제목을 반환 합니다.
        '''
        titles = []
        for tag in self.bs.select("table font.list_title"):
            titles.append(tag.text.strip())
        return titles

    def getLinks(self):
        '''
        게시글 별 본문 링크를 반환 합니다.
        '''
        links = []
        for tag in self.bs.select("table font.list_title"):
            links.append(urljoin(self.url, tag.find_parent()["href"]))
        return links

    def getImageLinks(self):
        '''
        게시글 별 섬네일 이미지 링크를 반환 합니다.
        '''
        imgLinks = []

        for tag in self.bs.select("table img.thumb_border"):
            imgLinks.append(urljoin(self.url, tag["src"]))

        return imgLinks

    def getImages(self):
        '''
        게시글 별 섬네일 이미지를 다운로드 하고, 저장된 파일 위치를 반환 합니다.

        이미지 저장 위치는 "images/ppomppu/" 폴더 아래에 현재
        "년-월-일_시간_분" 폴더를 만들고, 그 아래에 저장 됩니다.
        '''
        imgLinks = self.getImageLinks()

        # image/ppomppu 아래에 현재 시간("년-월-일_시간_분")으로 폴더 만들기
        now = datetime.now().isoformat()
        day_hour_minute = now[:10] + "_" + now[11:13] + "-" + now[14:16]
        path = "images/ppompu/" + day_hour_minute
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            raise os.OSError("(%s) 디렉토리를 만들 수 없습니다!" % (path))

        images = []

        for src in imgLinks:
            img = getDownload(src)
            imgName = src.split("/")[-1].split("?")[0]

            fileName = path + "/" + imgName

            with open(fileName, "wb") as f:
                f.write(img.content)
                images.append(fileName)

        return images

    def getReplyCounts(self):
        '''
        게시글 별 댓글 수를 반환 합니다.
        '''
        replyCounts = []

        for tag in self.bs.select("table font.list_title"):
            parent = tag.find_parent()
            if not parent.find_next_sibling():
                replyCounts.append(0)
            else:
                replyCount = parent.find_next_sibling().span.text.strip()
                replyCounts.append(int(replyCount))

        return replyCounts

    def getWriteDates(self):
        '''
        게시글 별 작성 일시를 반환 합니다.
        '''
        writeDates = []

        for tag in self.bs.select("td.eng.list_vspace"):
            if tag.has_attr("title"):
                writeDates.append(tag["title"])

        return writeDates

    def getLikeCounts(self):
        '''
        게시글 별 추천 회수를 반환 합니다.
        '''
        likes = []

        for intString in self.intStrings:
            if self.intStrings.index(intString) % 3 == 1:
                like = intString.split("-")[0].strip()
                if len(like) == 0:
                    likes.append(0)
                else:
                    likes.append(int(like))

        return likes

    def getQueryCounts(self):
        '''
        게시글별 조회 수를 반환 합니다.
        '''
        queryCounts = []

        for intString in self.intStrings:
            if self.intStrings.index(intString) % 3 == 2:
                if len(intString) == 0:
                    queryCounts.append(0)
                else:
                    queryCounts.append(int(intString))

        return queryCounts

    def getContentBodys(self):
        '''
        게시글 별 본문 내용을 반환 합니다.
        '''
        # 화면에서 결과를 보려면 아래 print 주석부분 해제
        contents = []
        links = self.getLinks()

        for link in links:
            html = getDownload(link)
            dom = BeautifulSoup(html.text, 'html.parser')

            board_contents = []
            # print("자유게시판 링크: ", link, end="\n\n")

            # 중복되는 class명에 대비해서, 태그명과 클래스명을 동시에 명기
            # (정확히 일치하는 tag만 찾음)
            for tag in dom.select("table.pic_bg td.han"):
                if len(tag.text.strip()) == 0:
                    continue
                else:
                    board_contents.append(tag.text.strip())

            if len(board_contents) != 0:
                # print("자유게시판 본문: \n", board_contents, end="\n\n")
                contents.append(board_contents)
            else:
                contents.append(None)

            # print(">" * 50, end="\n\n")

        return contents

    def getComments(self):
        '''
        게시글 별 Comments를 반환 합니다.

        //To-Do
        '''
        return None

    def getPpomppuBbs(self):
        '''
        뽐뿌게시판 전체 column을 리스트로 반환 합니다.
        
        번호, 분류, 글쓴이, 제목, 본문 링크, 이미지 링크, 이미지
        파일, 댓글 수, 작성일시, 추천 수, 조회 수, 게시글 본문, 댓글을
        List의 List로 반환 합니다.
        '''
        numbers = self.getNumbers()
        categorys = self.getCategorys()
        writers = self.getWriters()
        titles = self.getTitles()
        links = self.getLinks()
        imageLinks = self.getImageLinks()
        images = self.getImages()
        replyCounts = self.getReplyCounts()
        writeDates = self.getWriteDates()
        likes = self.getLikeCounts()
        queryCounts = self.getQueryCounts()
        contents = self.getContentBodys()
        comments = self.getComments()

        ppList = [
            numbers, categorys, writers, titles, links, imageLinks, images,
            replyCounts, writeDates, likes, queryCounts, contents, comments
        ]

        return ppList


class PpomppuFreeboard():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 자유게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self):
        self.url = "http://www.ppomppu.co.kr/zboard/zboard.php"
        self.param = {"id": "freeboard"}
        self.html = getDownload(self.url, self.param)
        self.bs = BeautifulSoup(self.html.text, "html.parser")

    def getNumbers(self):
        pass

    def getCategorys(self):
        pass

    def getWriters(self):
        pass

    def getTitles(self):
        pass

    def getUrls(self):
        pass

    def getImageLinks(self):
        pass

    def getImages(self):
        pass

    def getReplyCounts(self):
        pass

    def getWriteDates(self):
        pass

    def getLikeCounts(self):
        pass

    def getQueryCounts(self):
        pass

    def getReplyContents(self):
        pass

    def getComments(self):
        pass

    def getFreeboardList(self):
        pass
