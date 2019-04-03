'''
n-gram을 구현 합니다.
'''
import re
from string import punctuation

import numpy as np

from nltk.tokenize import word_tokenize
from konlpy.tag import Kkma


def ngramEojeol(sentence, n=2):
    '''
    어절 단위의 n-gram을 구현 합니다.

    어절 : 문장을 구성하고 있는 각각의 마디. 문장 성분의 최소 단위로서 띄어쓰기의 단위가 된다.

    sentence : string
    n : 어절 몇 개를 하나로 묶을지 지정하는 개수

    예)
    sentence: 단어1, 단어2, 단어3, 단어4  -> 4개
    출력(n=2) : 단어1 단어2, 단어2 단어3, 단어3 단어4 -> 3개 = 4개 - n개(2) + 1
    출력(n=3) : 단어1 단어2 단어3, 단어2 단어3 단어4  -> 2개 = 4개 - n개(3) + 1
    '''
    stopwords = ["이", "있", "하", "것", "들", "그", "되", "수", "이", "보", 
                "않", "없", "나", "사람", "주", "아니", "등", "같", "우리", 
                "때", "년", "가", "한", "지", "고", "전"]
    
    # 구두점 제거
    pattern = re.compile(r"[{0}]".format(re.escape(punctuation)))
    sentence = pattern.sub("", sentence)

    # tokenize
    tokens = np.array([token for token in np.array(word_tokenize(sentence)) if token not in stopwords])

    # Eojeol
    eojeol = np.array(list())
    
    for i in np.arange(len(tokens) - n + 1):
        eojeol = np.append(eojeol, "".join(tokens[i:i+n]))    # 단어 n 개를 붙여서 하나의 어절 생성
        
    return eojeol


# 음절 단위의 ngram (n=2)
def ngramUmjeol(term, n=2):
    '''
    음절 단위의 n-gram을 구현 합니다.

    음절 : 하나의 종합된 음의 느낌을 주는 말소리의 단위. 몇 개의 음소로 이루어지며, 
          모음은 단독으로 한 음절이 되기도 한다.

    term : string
    n : 음절 몇 개를 하나로 묶을지 지정하는 개수

    예)
    term : 음절1, 음절2, 음절3, 음절4  -> 4개
    출력(n=2) : 음절1 음절2, 음절2 음절3, 음절3 음절4 -> 3개 = 4개 - n개(2) + 1
    출력(n=3) : 음절1 음절2 음절3, 음절2 음절3 음절4  -> 2개 = 4개 - n개(3) + 1
    '''
    # 구두점 제거
    pattern = re.compile(r"[{0}]".format(re.escape(punctuation)))
    term = pattern.sub("", term)

    umjeol = np.array(list())
    
    for i in np.arange(len(term) - n + 1):
        umjeol = np.append(umjeol, "".join(term[i:i+n]))    # 공백 없이 붙여서 단어를 만듦
        
    return umjeol