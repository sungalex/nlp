'''
n-gram을 구현 합니다.
'''
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

    //To-Do: 띄어 쓰기 안되어 있는 경우에도, 단어/구두점 등을 구분할 수 있도록 수정 필요!!!
    //To-Do: 공백/개행문자 등 제거!!!
    '''
    tokens = word_tokenize(sentence)
    ngram = []
    
    for i in range(len(tokens) - n + 1):
        ngram.append(" ".join(tokens[i:i+n]))    # 공백을 추가해줘야 단어 사이가 구분됨
        
    return ngram


# 음절 단위의 ngram (n=2)
def ngramUmjeol(term, n=2):
    '''
    음절 단위의 n-gram을 구현 합니다.

    음절 : 하나의 종합된 음의 느낌을 주는 말소리의 단위.몇 개의 음소로 이루어지며, 
          모음은 단독으로 한 음절이 되기도 한다.

    term : string
    n : 음절 몇 개를 하나로 묶을지 지정하는 개수

    예)
    term : 음절1, 음절2, 음절3, 음절4  -> 4개
    출력(n=2) : 음절1 음절2, 음절2 음절3, 음절3 음절4 -> 3개 = 4개 - n개(2) + 1
    출력(n=3) : 음절1 음절2 음절3, 음절2 음절3 음절4  -> 2개 = 4개 - n개(3) + 1
    '''
    ngram = []
    
    for i in range(len(term) - n + 1):
        ngram.append("".join(term[i:i+n]))    # 공백 없이 붙여서 단어를 만듦
        
    return ngram