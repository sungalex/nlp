'''
naver.py : Naver 실시간 주요 News Scraping

'''
from functions.download import getDownload
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
from datetime import datetime
import numpy as np
import pandas as pd

class NewsScraping():
    def __init__(self):
        self.url = "https://news.naver.com/"
        self.html = getDownload(self.url)
        self.dom = BeautifulSoup(self.html.text, "html.parser")
        self.categoryNames = []
        self.newsLists = []    # 6개 카테고리, 10개 기사, 제목과 링크
        self.path = ""
        self.fileNames = []
        self.articles = ""     # 다운로드 한 기사 내용

    def getCategorys(self):
        '''
        6개 카테고리 리스트 찾기
        ['정치', '경제', '사회', '생활문화', '세계', 'IT과학']
        '''
        self.categoryNames = []

        for cat in self.dom.select(".category"):
            for aTag in cat.find_all("a"):
                self.categoryNames.append(aTag.text.strip())

        self.categoryNames = [cat.replace('/', '') for cat in self.categoryNames]

        return self

    def getNewsLists(self):
        '''
        카테고리별 뉴스 리스트 찾기
        '''
        self.newsLists = []

        # id가 ranking_100 ~ ranking_105인 태그 아래에 섹션별로 내용이 있음
        for section in self.dom.select("[id^='ranking_10']"):
            sectionNews = []
            for li in section.find_all("li"):
                # li 태그 아래 em 태그에 순번이 저장되어 있음
                # (순번 제외하고 저장하기 위해 li.find("a").text 사용. 순번까지 저장하려면 li.text 사용)
                # sectionNews.append([li.find("a").text.strip(), urljoin(self.url, li.find("a")["href"])])
                sectionNews.append([li.text.strip(), urljoin(self.url, li.find("a")["href"])])
    
            # 섹션별로 구분해서 제목과 링크를 저장함(3차원 배열 : 섹션, 기사, 제목/링크)
            self.newsLists.append(sectionNews)

        return self

    def makeSaveDir(self):
        '''
        naver_news 아래에 현재 시간("년-월-일_시간_분")으로 폴더 만들기
        '''
        now = datetime.now().isoformat()
        day_hour_minute = now[:10] + "_" + now[11:13] + "-" + now[14:16]
        self.path = "naver_news/" + day_hour_minute

        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            return self
        except:
            print("(%s) 디렉토리를 만들 수 없습니다!" % (self.path))
            return None
    
    def saveArticles(self):
        '''
        기사 다운로드 후 본문을 저장하고, 기사 제목과 url을 csv 파일로 저장하기
        '''
        if len(self.path) == 0 or os.path.exists(self.path) == False:
            self.makeSaveDir()

        for section in self.newsLists:
            # 파일명에 사용할 카테고리 이름 가져오기
            cat = self.categoryNames[self.newsLists.index(section)]

            # 기사 다운로드 하고 가져오기
            for sec in section:
                # sec[0]에 기사 제목, sec[1]에 기사 링크가 있음
                html = getDownload(sec[1])
                dom = BeautifulSoup(html.text, "html.parser")
                contents = dom.select("#articleBodyContents")[0]

                # content에 <script> 태그 내의 내용이 포함되어 있음 (삭제할 필요는 없음. 삭제하지 않으려면 위에 코멘트 처리된 부분을 사용)
                contents_ = contents.text.replace("// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}", "")
 
                # 기사 url에 포함된 article ID(aid) 값을 추출해서 file명에 사용
                aid = re.findall(r"aid=\d+", sec[1])[0].split("=")[1]
                fileName = cat + "-" + aid + ".txt"        
                fullPath = os.path.join(self.path, fileName)

                with open(fullPath, "w") as f:
                    f.write(contents_)

        csvFileName = "naver_news/newslist-" + self.path.split("/")[1] + ".csv"
        df = pd.DataFrame(np.array(self.newsLists).reshape(-1, 2))
        df.to_csv(csvFileName, header=False, index=False)

        return self

    def getPath(self):
        if self.path == "":
            dirs_ = []
            for entry in os.listdir("naver_news/"):
                if os.path.isdir(os.path.join("naver_news/", entry)) == True:
                    dirs_.append(entry)

            dirs_.sort()
            self.path = "naver_news/" + dirs_[-1]

        return self

    def getFilenames(self):
        '''
        가장 최근 저장된 뉴스 기사 폴더 이름을 포함한 파일명 찾기
        '''
        self.fileNames = []

        self.getPath()
        files = os.listdir(self.path)

        for file in files:
            self.fileNames.append(os.path.join(self.path, file))

        return self
    
    def getArticles(self, section='all'):
        '''
        다운로드 한 기사 내용 읽어오기

        section을 지정하면 해당 section의 기사 만 읽어오고, 지정하지 않으면 전체 기사 내용을 읽어옮
        {'정치', '경제', '사회', '생활문화', '세계', 'IT과학', 'all'}
        '''
        self.articles = ""

        self.getPath()
        self.getFilenames()
        
        if section == "all":
            sections = self.categoryNames
        else:
            sections = [section]

        for fileName in self.fileNames:
            sec = fileName.split("/")[-1].split("-")[0]
            if sec in sections:
                with open(fileName, "r") as f:
                    self.articles += f.read() + "\n"
            else:
                continue

        return self

    def loadNewsList():
        '''
        최근 저장된 뉴스 기사 리스트 읽어오기
        '''

        return self