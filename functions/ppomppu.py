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
import numpy as np


class Ppomppu():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 뽐뿌게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self, category=None):
        '''
        Ppomppu 게시판 객체를 생성합니다.
        
        객체 생성 시 category 값을 전달하면, 해당 category 게시글만 List 됩니다.
        category를 지정하지 않으면 전체 게시글이 List 됩니다.
        
        category 값은 아래와 같습니다.
            1:기타
            4~6:컴퓨터,디니털,먹거리
            8~13:서적,가전/가구,육아,카메라,의류/잡화,화장품
            15:등산/캠핑

        '''
        self.url = "http://www.ppomppu.co.kr/zboard/zboard.php"
        self.param = {"id": "ppomppu"}
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

        for tag in self.bs.select("td.list_vspace .list_name > a"):
            if len(tag.text.strip()) == 0:
                writers.append(tag.find("img")["alt"])
            else:
                writers.append(tag.text.strip())

        return writers

    def getTitles(self):
        '''
        게시글 별 제목을 반환 합니다.
        '''
        titles = []

        for tag in self.bs.select("td.list_vspace a > font"):
            titles.append(tag.text.strip())

        return titles

    def getLinks(self):
        '''
        게시글 별 본문 링크를 반환 합니다.
        '''
        links = []

        for tag in self.bs.select("td.list_vspace a > font"):
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

        for tag in self.bs.select("td.list_vspace td > span"):
            if len(tag.text.strip()) == 0:
                replyCounts.append(0)
            else:
                replyCounts.append(int(tag.text.strip()))

        return replyCounts

    def getWriteDates(self):
        '''
        게시글 별 작성 일시를 반환 합니다.
        '''
        writeDates = []

        for tag in self.bs.select("td.eng.list_vspace > .eng.list_vspace"):
            if tag.find_parent().has_attr("title"):
                writeDates.append(tag.find_parent()["title"])
            else:
                 writeDates.append(None)

        del writeDates[0]    # 0번째 원소(공지 글 등록일)는 제외해야 함

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

    def getContents(self):
        '''
        게시글 별 Content 본문 DOM 형태로 반환 합니다.
        '''
        contents = []
        links = self.getLinks()

        for link in links:
            html = getDownload(link)
            dom = BeautifulSoup(html.text, 'html.parser')
            contents.append(dom)

        return contents

    def getContentBodys(self):
        '''
        게시글 별 본문 내용을 반환 합니다.
        
        본문이 2차원 배열 형태로 저장되어 있으며, 본문 하나가 1차원 배열로(<p> 태그의 단락을 하나의 원소로) 저장되어 있습니다.
        '''

        contentBodys = []
        contents = self.getContents()

        for dom in contents:
            body = []
            for p in dom.select("table.pic_bg td.board-contents p"):
                if len(p.text.strip()) != 0:
                    body.append(p.text.strip())

            contentBodys.append(body)

        return contentBodys

    def getComments(self):
        '''
        게시글 별 Comments를 반환 합니다.

        # [댓글 구조]
        # div.comment_wrapper : 맨 상위 레벨 댓글들을 감싸고 있는 wrapper
        # div.comment_line : 해당 레벨의 실제 댓글이 포함된 태그 (댓글의 레벨에 상관 없이 태크.클래스명이 동일함)
        # 댓글의 서브 댓글은 해당 댓글을 나타내는 div.comment_line의 다음 다음 sibling div에 있음
        # 서브 댓글이 있는 댓글은 div.comment_line의 siblings에 div가 있음
        #
        # 댓글 구조
        # div.comment_wrapper                   --> 맨 상위 레벨 댓글들을 감싸고 있는 wrapper
        #    - div.comment_div0
        #        - div.comment_line             --> 해당 레벨의 댓글이 포함되어 있음 (맨 상위 레벨 댓글)
        #            ---- div.han               --> 실제 댓글 본문
        #        - div
        #        - div                          --> 서브 댓글이 없는 경우 Null (태그가 없거나 내용이 없음)
        #            - div.comment_line         --> 해당 레벨의 댓글이 포함되어 있음
        #                ---- div.han           --> 실제 댓글 본문
        #            - div
        #            - div                      --> 서브 댓글이 없는 경우 Null (태그가 없거나 내용이 없음)
        #                - div.comment_line     --> 해당 레벨의 댓글이 포함되어 있음
        #                    ---- div.han       --> 실제 댓글 본문
        #                - div
        #                - div
        #
        # 실제 댓글 본문은 div.comment_line 아래 div.han에 있음
        # 댓글 본문을 가져오려면 : dom.select("div.comment_wrapper div.han"), dom.select("div#newbbs div.han"),
        #                    dom.select("div.comment_line div.han"), dom.select("div.han") 등 선택적으로 사용 가능
        # 전체 댓글을 계층적으로 읽어오려면 : //To-To
        '''

        comments = []
        contents = self.getContents()

        for dom in contents:
            if len(dom.select("div.comment_line div.han")) != 0:
                comment = []

                for comment_ in dom.select("div.comment_line div.han"):
                    if len(comment_.text.strip()) != 0:
                        comment.append(comment_.text.strip())

            comments.append(comment)
        
        return comments

    def getPpomppuBbs(self):
        '''
        뽐뿌게시판 전체 column을 리스트로 반환 합니다.
        
        번호, 분류, 글쓴이, 제목, 본문 링크, 이미지 링크, 이미지 저장 위치, 
        댓글 수, 작성일시, 추천 수, 조회 수를 2차원 numpy 배열로 반환 합니다.
        '''
        numbers = np.array(self.getNumbers())
        categorys = np.array(self.getCategorys())
        writers = np.array(self.getWriters())
        titles = np.array(self.getTitles())
        links = np.array(self.getLinks())
        imageLinks = np.array(self.getImageLinks())
        images = np.array(self.getImages())
        replyCounts = np.array(self.getReplyCounts())
        writeDates = np.array(self.getWriteDates())
        likes = np.array(self.getLikeCounts())
        queryCounts = np.array(self.getQueryCounts())
        # contents = np.array(self.getContentBodys())
        # comments = np.array(self.getComments())

        ppomppu = np.array([
            numbers, categorys, writers, titles, links, imageLinks, images,
            replyCounts, writeDates, likes, queryCounts])

        return np.vstack(ppomppu.T)


class PpomppuFreeboard():
    '''
    뽐뿌(http://www.ppomppu.co.kr) 사이트의 자유게시판 정보를 추출하기 위한
    함수들을 포함하고 있습니다.
    '''

    def __init__(self):
        '''
        Freeboard 게시판 객체를 생성합니다.
        '''
        self.url = "http://www.ppomppu.co.kr/zboard/zboard.php"
        self.param = {"id": "freeboard"}
        self.html = getDownload(self.url, self.param)
        self.bs = BeautifulSoup(self.html.text, "html.parser")
        self.intStrings = self.list_vspace_select()[0]
        self.writeDates = self.list_vspace_select()[1]

    def list_vspace_select(self):
        '''
        "td.eng.list_vspace" 클래스명으로 나타나는 값들을 일괄 추출하여 반환 합니다.

        writeDates는 getWriteDates()에서 사용 합니다.
        
        숫자형 데이터인 3개의 열은 구분할 만한 ID/Class 정보가 없기 때문에 한꺼번에 추출 후
        순서에 따하 해당 컬럼 자료로 분류해서 사용 합니다.
        첫번째 자료는 "번호", 두번째 자료는 "추천", 세번째 자료는 "조회수"를
        의미 합니다. getNumbers(), getLikeCounts(), getQueryCounts() 함수에서
        이 값을 사용합니다.

        이 함수는 객체 생성 시 호출됩니다.
        '''
        intStrings = []
        writeDates = []

        for list_vspace in self.bs.select("td.eng.list_vspace"):
            if list_vspace.has_attr("title"):    # 등록일
                writeDates.append(list_vspace["title"])
            else:           # 번호(0), 추천 수(1), 조회 수(2)
                if len(list_vspace.text.split("-")[0].strip()) != 0:
                    intStrings.append(list_vspace.text.split("-")[0].strip())
                else:
                    intStrings.append("0")

        del writeDates[0]    # 공지글 작성일 삭제
        del intStrings[0:2]    # 공지글 추천 수, 조회 수 삭제 (공지글 번호는 없음)

        return intStrings, writeDates

    def getNumbers(self):
        '''
        게시글 번호를 반환 합니다.
        '''
        numbers = []

        for intString in self.intStrings:
            if self.intStrings.index(intString) % 3 == 0:
                numbers.append(intString)

        return numbers

    def getWriters(self):
        '''
        게시글 별 글쓴이 필명을 반환 합니다.
        '''
        writers = []

        for tag in self.bs.select("td.list_vspace .list_vspace > a"):
            if len(tag.text.strip()) == 0:
                writers.append(tag.find("img")["alt"])
            else:
                writers.append(tag.text.strip())

        del writers[0]

        return writers

    def getTitles(self):
        '''
        게시글 별 제목을 반환 합니다.
        '''
        titles = []

        for tag in self.bs.select("td.list_vspace a > font"):
            titles.append(tag.text.strip())

        return titles

    def getLinks(self):
        '''
        게시글 별 본문 링크를 반환 합니다.
        '''
        links = []

        for tag in self.bs.select("td.list_vspace a > font"):
            links.append(urljoin(self.url, tag.find_parent()["href"]))

        return links

    def getReplyCounts(self):
        '''
        게시글 별 댓글 수를 반환 합니다.
        '''
        replyCounts = []

        for tag in self.bs.select("td.list_vspace > a"):
            if tag.find_next_sibling("span") is None:
                replyCounts.append(0)
            else:
                replyCounts.append(len(tag.find_next_sibling("span").text.strip()))

        del replyCounts[0]

        return replyCounts

    def getWriteDates(self):
        return self.writeDates

    def getLikeCounts(self):
        '''
        게시글 별 추천 회수를 반환 합니다.
        '''
        likes = []

        for intString in self.intStrings:
            if self.intStrings.index(intString) % 3 == 1:
                if len(intString) == 0:
                    likes.append(0)
                else:
                    likes.append(int(intString))

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

    def getContents(self):
        '''
        게시글 별 Content 본문 DOM 형태로 반환 합니다.
        '''
        contents = []
        links = self.getLinks()

        for link in links:
            html = getDownload(link)
            dom = BeautifulSoup(html.text, 'html.parser')
            contents.append(dom)

        return contents

    def getContentBodys(self):
        '''
        게시글 별 본문 내용을 반환 합니다.
        
        본문이 2차원 배열 형태로 저장되어 있으며, 본문 하나가 1차원 배열로(<p> 태그의 단락을 하나의 원소로) 저장되어 있습니다.
        '''

        contentBodys = []
        contents = self.getContents()

        for dom in contents:
            body = []
            for p in dom.select("table.pic_bg td > p"):
                #print(p)
                if len(p.text.strip()) != 0:
                    body.append(p.text.strip())

            contentBodys.append(body)

        return contentBodys

    def getComments(self):
        '''
        게시글 별 Comments를 반환 합니다.

        # [댓글 구조]
        # div.comment_wrapper : 맨 상위 레벨 댓글들을 감싸고 있는 wrapper
        # div.comment_line : 해당 레벨의 실제 댓글이 포함된 태그 (댓글의 레벨에 상관 없이 태크.클래스명이 동일함)
        # 댓글의 서브 댓글은 해당 댓글을 나타내는 div.comment_line의 다음 다음 sibling div에 있음
        # 서브 댓글이 있는 댓글은 div.comment_line의 siblings에 div가 있음
        #
        # 댓글 구조
        # div.comment_wrapper                   --> 맨 상위 레벨 댓글들을 감싸고 있는 wrapper
        #    - div.comment_div0
        #        - div.comment_line             --> 해당 레벨의 댓글이 포함되어 있음 (맨 상위 레벨 댓글)
        #            ---- div.han               --> 실제 댓글 본문
        #        - div
        #        - div                          --> 서브 댓글이 없는 경우 Null (태그가 없거나 내용이 없음)
        #            - div.comment_line         --> 해당 레벨의 댓글이 포함되어 있음
        #                ---- div.han           --> 실제 댓글 본문
        #            - div
        #            - div                      --> 서브 댓글이 없는 경우 Null (태그가 없거나 내용이 없음)
        #                - div.comment_line     --> 해당 레벨의 댓글이 포함되어 있음
        #                    ---- div.han       --> 실제 댓글 본문
        #                - div
        #                - div
        #
        # 실제 댓글 본문은 div.comment_line 아래 div.han에 있음
        # 댓글 본문을 가져오려면 : dom.select("div.comment_wrapper div.han"), dom.select("div#newbbs div.han"),
        #                    dom.select("div.comment_line div.han"), dom.select("div.han") 등 선택적으로 사용 가능
        # 전체 댓글을 계층적으로 읽어오려면 : //To-To
        '''

        comments = []
        contents = self.getContents()

        for dom in contents:
            if len(dom.select("div.comment_line div.han")) != 0:
                comment = []

                for comment_ in dom.select("div.comment_line div.han"):
                    if len(comment_.text.strip()) != 0:
                        comment.append(comment_.text.strip())

                comments.append(comment)
        
        return comments

    def getFreeboard(self):
        '''
        자유게시판 전체 column을 리스트로 반환 합니다.
        
        번호, 글쓴이, 제목, 본문 링크, 댓글 수, 작성일시, 추천 수, 조회 수를
        2차원 numpy 배열로 반환 합니다.
        '''
        numbers = np.array(self.getNumbers())
        writers = np.array(self.getWriters())
        titles = np.array(self.getTitles())
        links = np.array(self.getLinks())
        replyCounts = np.array(self.getReplyCounts())
        writeDates = np.array(self.getWriteDates())
        likes = np.array(self.getLikeCounts())
        queryCounts = np.array(self.getQueryCounts())
        # contents = np.array(self.getContentBodys())
        # comments = np.array(self.getComments())

        ppomppu = np.array([numbers, writers, titles, links,
                  replyCounts, writeDates, likes, queryCounts])

        return np.vstack(ppomppu.T)