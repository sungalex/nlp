'''
naver.py : Naver 실시간 주요 News Scraping을 위한 메서드를 정의 합니다.

외부에서 직접 호출이 필요한 메서드 외에 다른 메서드 및 속성들은 
명칭에 "underscore"을 prefix로 추가해서 숨김(private) 처리 했습니다.
'''
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from functions.download import getDownload


class NewsScraping():

    def __init__(self):
        self._url = "https://news.naver.com/"
        self._html = getDownload(self._url)
        self._dom = BeautifulSoup(self._html.text, "html.parser")
        self._category_names = ['정치', '경제', '사회', '생활문화', '세계', 'IT과학']
        self._category_codes = {
            self._category_names[0]: "00",
            self._category_names[1]: "01",
            self._category_names[2]: "02",
            self._category_names[3]: "03",
            self._category_names[4]: "04",
            self._category_names[5]: "05"}
        self.ranks = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'}
        self._path = ""
        self._newslists = []    # 6개 카테고리, 10개 기사, 랭크/제목/링크
        self._filenames = []    # 저장된 파일 리스트
        self._articles = ""    # 다운로드 한 기사 전체 내용(지정한 섹션 기사)
        self._article = ""    # 다운로드 한 기사 1건

    def _get_categorys(self):
        '''
        주요 뉴스 카테고리 리스트를 찾습니다.
        ['정치', '경제', '사회', '생활문화', '세계', 'IT과학']
        '''
        self._category_names = []

        for cat in self._dom.select(".category"):
            for aTag in cat.find_all("a"):
                self._category_names.append(aTag.text.strip())

        # 카테고리 이름에 "/"가 있는 경우 제거 합니다.
        self._category_names = [
            cat.replace('/', '') for cat in self._category_names
        ]

        return self

    def _get_newslists(self):
        '''
        카테고리별 뉴스 리스트 찾습니다.
        '''
        self._newslists = []

        # id가 ranking_100 ~ ranking_105인 태그 아래에 섹션별로 내용이 있음
        for section in self._dom.select("[id^='ranking_10']"):
            sectionNews = []
            for li in section.find_all("li"):
                # li 태그 아래 em 태그에 순번이 저장되어 있음
                rank = li.find("em").text.strip()
                title = li.find("a").text.strip()
                url = urljoin(self._url, li.find("a")["href"])
                sectionNews.append([rank, title, url])

            # 섹션별로 구분해서 제목과 링크를 저장함
            # (3차원 배열 : 섹션, 기사, 랭크/제목/링크)
            self._newslists.append(sectionNews)

        return self

    def _make_savedir(self):
        '''
        naver_news 아래에 현재 시간("년-월-일_시간_분")으로 폴더를 만듭니다.
        '''
        now = datetime.now().isoformat()
        day_hour_minute = now[:10] + "_" + now[11:13] + "-" + now[14:16]
        self._path = "naver_news/" + day_hour_minute

        try:
            if not os.path.exists(self._path):
                os.makedirs(self._path)
            return self
        except:
            print("(%s) 디렉토리를 만들 수 없습니다!" % (self._path))
            return None

    def download(self):
        '''
        기사 다운로드 후 본문을 저장하고, 기사 랭크, 제목, url을 csv 파일로 저장합니다.

        기사 저장 파일명은 category_code(00~05) + "-" + rank(00~09) + "-" + 
        aid + ".txt" 형태로 저장합니다.
        csv 파일명은 "newslist-" + path + ".csv" 형태로 저장합니다.
        
        return : 뉴스 기사 리스트를 3차원 배열(섹션, 기사, 랭크/제목/링크)로 반환 합니다.
        '''
        self._get_categorys()
        self._get_newslists()
        self._make_savedir()

        for idx, section in enumerate(self._newslists):
            # 파일명에 사용할 카테고리 이름 가져오기
            # idx = self._newslists.index(section)
            cat_code = self._category_codes[self._category_names[idx]]

            # 기사 다운로드 하고 가져오기
            for sec in section:
                # sec[0]에 rank, sec[1]에 기사 제목, sec[2]에 기사 링크가 있음
                html = getDownload(sec[2])
                dom = BeautifulSoup(html.text, "html.parser")
                contents = dom.select("#articleBodyContents")[0]

                # content에 <script> 태그 내의 내용이 포함되어 있음 
                # (삭제할 필요는 없음. 삭제하지 않으려면 위에 코멘트 처리된 부분을 사용)
                contents_ = contents.text.replace(
                    "// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}",
                    "")

                # 기사 url에 포함된 article ID(aid) 값을 추출해서 file명에 사용
                aid = re.findall(r"aid=\d+", sec[2])[0].split("=")[1]
                rank = sec[0]
                fileName = cat_code + "-" + self.ranks[rank] + "-" + aid + ".txt"
                fullPath = os.path.join(self._path, fileName)

                with open(fullPath, "w") as f:
                    f.write(contents_)

        csvFileName = "naver_news/newslist-" + self._path.split(
            "/")[-1] + ".csv"
        df = pd.DataFrame(np.array(self._newslists).reshape(-1, 3))
        df.to_csv(csvFileName, header=False, index=False)

        return self._newslists

    def _get_path(self):
        '''
        가장 최근 날짜의 폴더를 path로 선택 합니다.
        '''
        if self._path == "":
            _dirs = []
            for entry in os.listdir("naver_news/"):
                if os.path.isdir(os.path.join("naver_news/", entry)) == True:
                    _dirs.append(entry)

            _dirs.sort()
            self._path = "naver_news/" + _dirs[-1]

        return self

    def get_filenames(self):
        '''
        가장 최근 저장된 뉴스 기사 폴더 이름을 포함한 파일명 리스트를 반환 합니다.
        '''
        self._filenames = []

        self._get_path()
        files = os.listdir(self._path)

        for file in files:
            self._filenames.append(os.path.join(self._path, file))

        self._filenames.sort()

        return self._filenames

    def get_articles(self, section=None):
        '''
        다운로드 한 기사 내용을 읽어옵니다.

        section을 지정하면 해당 section의 기사 만 읽어오고, 
        지정하지 않으면 전체 기사 내용을 읽어옵니다.
        section은 {'정치', '경제', '사회', '생활문화', '세계', 'IT과학'} 중 하나 입니다.

        return: 지정한 섹션의 전체 기사 내용을 문자열 형태로 반환 합니다.
        '''
        self._articles = ""

        self.get_filenames()

        if section is None:
            sections = ['00', '01', '02', '03', '04', '05']
        else:
            sections = [self._category_codes[section]]

        for fileName in self._filenames:
            sec = fileName.split("/")[-1].split("-")[0]
            if sec in sections:
                with open(fileName, "r") as f:
                    self._articles += f.read() + "\n"
            else:
                continue

        return self._articles

    def get_article(self, section='경제', n_articles=1):
        '''
        다운로드 한 기사 내용 중 지정한 섹션의 첫번째 기사를 읽어옵니다.

        n_articles를 지정하면, 상위 랭크 기사를 지정한 개수 만큼 읽어옵니다.

        section은 {'정치', '경제', '사회', '생활문화', '세계', 'IT과학'} 
        중 하나를 지정합니다.

        return: 지정한 섹션의 첫번째 기사 내용을 문자열 형태로 반환 합니다.
        '''
        self._article = ""
        n_ranks = []
        for rank in range(1, n_articles + 1):
            n_ranks.append(self.ranks[str(rank)])

        self.get_filenames()

        for fileName in self._filenames:
            code = fileName.split("/")[-1].split("-")[0:2] #[0]:섹션코드, [1]:rank
            if code[0] == self._category_codes[section] and code[1] in n_ranks:
                with open(fileName, "r") as f:
                    self._article += f.read() + "\n"
            else:
                continue

        return self._article