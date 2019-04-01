'''
본 코드는 IPA 인공지능(언어지능) 교육 과정의 프로젝트 산출물 입니다.
Information Retrieval(정보검색) 관련 함수를 정의 합니다.

버지니아대학의 "CS 4501: Information Retrieval" 과정을 참고하여 색인, 질의 관련 함수를 구현 했습니다.
버지니아대학 강의 사이트 : http://www.cs.virginia.edu/~hw5x/Course/IR2015/_site/lectures/
'''
import re
from string import punctuation
from collections import defaultdict
from math import log10

from konlpy.corpus import kobill
from konlpy.tag import Kkma

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import gutenberg

from functions.nlp import ngram


def raw_tf(freq):
    '''
    return: freq
    '''
    return freq


def norm_tf(freq, total_count):
    '''
    return: freq / total_count
    '''
    return freq / total_count


def log_tf(freq):
    '''
    return: 1+log10(freq), if freq > 0
            0, otherwise
    '''
    if freq > 0:
        return 1+log10(freq)
    else:
        return 0


def max_tf(freq, max_freq, alpha=0.5):
    '''
    alpha(0<alpha<1)와 1 사이의 값으로 정규화 됨 (double normalization K)
    return: alpha + (1-alpha) * (freq / max_freq)
    '''
    return alpha + (1-alpha) * (freq / max_freq)


def raw_idf(df, n):
    '''
    # 일반적인 IDF
    return: log10(n/df)
    '''
    return log10(n/df)


def smoothig_idf(df, n):
    '''
    return: log10((n+1)/df)
    '''
    return log10((n+1)/df)


def probability_idf(df, n):
    '''
    return: log10((n-df+1)/df)    # N - df가 0이 되는 것을 방지하기 위해 1을 더함
    '''
    return log10((n-df+1)/df)


def get_lexicon(corpus=kobill):
    '''
    corpus 데이터를 인수로 받아서, 공백으로 분리한 lexicon을 반환 합니다.
    인수 corpus에는 corpus 객체를 전달 합니다.
    default로 konlpy 패키지의 kobill(의안) 자료를 lexicon으로 반환 합니다.

    사용예)
        from konlpy.corpus import kolaw
        from functions.info_retrieval import get_lexicon

        lexicon = get_lexicon(corpus=kolaw)
    '''
    lexicon = set()

    for document in corpus.fileids():
        content = corpus.open(document).read()

        for token in content.split():
                lexicon.add(token)
                
    return list(lexicon)


def get_dtm_from_konlpy(corpus=kobill, k_morpheme=Kkma):    # Document-Term Metrix
    '''
    한국어 형태소 분석기를 이용(default로 Kkma 사용)해서, document-term matrix를 만듭니다.

    # dictionary 내에 dictionary를 포함하고 있는 구조
        {"document1": {"term1": frequency1,
                       "term2": frequency2,
                          ...
                      }
         "document2": {... 
                      }
         ...
        }
    '''
    dtm = defaultdict(lambda: defaultdict(int))

    morpheme = k_morpheme().morphs

    for document in corpus.fileids():
        content = corpus.open(document).read()
        
        for sentence in sent_tokenize(content):
            for morph in morpheme(sentence):
                if dtm[document][morph] is None:
                    dtm[document][morph] = 1
                else:
                    dtm[document][morph] += 1
        
    return dtm


def get_dtm_from_nltk(corpus=gutenberg, e_tokenize=word_tokenize):    # Document-Term Metrix
    '''
    영어 형태소 분석기를 이용(default로 work_tokenize를 사용)해서, document-term matrix를 만듭니다.

    # dictionary 내에 dictionary를 포함하고 있는 구조
        {"document1": {"term1": frequency1,
                       "term2": frequency2,
                          ...
                      }
         "document2": {... 
                      }
         ...
        }
    '''
    dtm = defaultdict(lambda: defaultdict(int))

    for document in corpus.fileids():
        content = corpus.open(document).read()
        
        for token in word_tokenize(content):
            if dtm[document][token] is None:
                dtm[document][token] = 1
            else:
                dtm[document][token] += 1
        
    return dtm


def get_remove_pattern():
    '''
    corpus에서 제거할 문자의 정규표현식이 dictionary로 작성 되어 있습니다.

    사용예)
        corpus = get_remove_pattern()["email"].sub(" ", corpus)
    '''
    patterns = {}
    patterns["email"] = re.compile(r"(\w+@[a-zA-Z0-9\-\_]{3,}(.[a-zA-Z]{2,})+)")
    patterns["url"] = re.compile(r"^(https?:\/\/)?([\w\d-]{3,}(.[a-zA-Z]{2,})+)$")
    patterns["maxlength"] = re.compile(r"\b[\w\dㄱ-ㅎㅏ-ㅣ가-힣]{8,}\b")
    patterns["numeric"] = re.compile(r"\b(\d{1}|\d{5,})\b")
    patterns["non_word"] = re.compile(r"\b[^\w\dㄱ-ㅎㅏ-ㅣ가-힣]{2,}\b")
    patterns["whitespace"] = re.compile(r"\s{2,}|(\\n){2,}")
    patterns["punctuation"] = re.compile(r"[%s]{2,}" % re.escape(punctuation))
    patterns["non_korean"] = re.compile(r"([^ㄱ-ㅎㅏ-ㅣ가-힣]+)")

    return patterns


def clean_collection(collection):
    '''
    collection의 content에 포함된 email, url, 8자 이상의 글자, 숫자(1글자 또는 5자 이상), 
    Non_Word, white space 등을 제거하고 Cleaned collection을 반환 합니다.
    '''
    cleaned_collection = list()

    for document_name, content in collection:
        cleaned_content = get_remove_pattern()["email"].sub(" ", content)
        cleaned_content = get_remove_pattern()["url"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["maxlength"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["numeric"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["non_word"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["whitespace"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["punctuation"].sub(" ", cleaned_content)

        cleaned_collection.append((document_name, cleaned_content))

    return cleaned_collection


def extend_lexicon(corpus):
    '''
    collection의 document별 content(전처리 된 content)를 받아서 token의 수를 늘려서 lexicon을 반환 합니다.
        --> token = 어절 + 형태소 + 명사 + 바이그램(음절)
    '''
    extended_lexicon = list()
    dictTerm = list()
    dictPOS = list()
    dictNoun = list()
    dictNgram = list()

    kkma = Kkma()
    
    for token in corpus.split():
        if len(token) > 1:
            dictTerm.append(token)
            dictPOS.extend([morpheme for morpheme in kkma.morphs(token) if len(morpheme) > 1])
            dictNoun.extend([noun for noun in kkma.nouns(token) if len(noun) > 1])
            dictNgram.extend(ngram.ngramUmjeol(token))

    extended_lexicon.extend(dictTerm)
    extended_lexicon.extend(dictPOS)
    extended_lexicon.extend(dictNoun)
    extended_lexicon.extend(dictNgram)

    return extended_lexicon


def inverted_index_with_tf(collection):
    '''
    lexicon으로 부터 document에 빠르게 access 할 수 있도록, posting file을 만들어 줍니다.
    (lexicon -> posting_file -> document)

    # collection은 tuple(document이름, content)들의 리스트 입니다. content는 lexicon list 입니다.
    # collection = [
    #       ("document1", content1),
    #       ("document2", content2),
    #       ...
    #   ]

    # global_lexicon => dictionary: {단어1:포스팅위치, 단어2:포스팅위치, ...}
    #   -> 동일한 단어가 여러 번 나온 경우 마지막 나온 global_posting 위치
    #   -> global_posting data를 생성 후 global_posting의 list index를 포스팅 위치로 저장

    # global_document => list: [0:문서1, 1:문서2, ...]
    #   -> document 목록이 순서대로 저장되어 있음(list의 저장된 위치를 index로 사용)

    # global_posting => list: [0:[단어 idx, 문서 idx, 빈도, 다음주소],
    #                          1:[단어 idx, 문서 idx, 빈도, 다음주소],
    #                          ...
    #                         ]
    #   -> 동일한 term의 첫번째 posting_data에는 다음주소 부분에 "None" 값 할당
    #   -> global_lexicon이 마지막 posting_data의 index 값을 저장하고 있음
    #   -> global_posting의 빈도는 tf(Term Frequency) : max_tf 값
    #   -> evaluate_idf()로 idf 값을 계산 시, global_posting(posting_data)의 빈도에 tfidf 값이 할당됨
    '''
    global_lexicon = dict()
    global_document = list()
    global_posting = list()
    dtm = defaultdict(lambda: defaultdict(int))
    posting_idx = 0

    for doc_idx, (document_name, lexicon) in enumerate(collection):
        # pointer 대체용으로 doc_idx를 만든다. (document_name 이름은 절대로 겹치지 않는다는 가정)
        # for 루프를 반복할 때마다, global_document의 크기와 doc_idx가 1씩 증가
        global_document.append(document_name)

        # 로컬 영역
        # local_posting => {term1: 빈도, term2: 빈도, ...}
        local_posting = dict()

        # if 문을 없애기 위해, 0으로 채워진 local_posting을 먼저 만든 후,
        # term이 발생할 때 마다 1씩 더해주는 방식으로 for 문을 두번 반복
        # dtm도 local_posting을 만들 때 같은 로직으로 생성
        for term in lexicon:
            local_posting[term] = 0
            dtm[document_name][term] = 0

        for term in lexicon:
            local_posting[term] += 1
            dtm[document_name][term] += 1

        max_freq = max(local_posting.values())

        for term, freq in local_posting.items():
            before_idx = global_lexicon.get(term, None)    # lexicon이 마지막으로 추가된 posting 위치 가져오기
            global_lexicon[term] = posting_idx    # 해당 lexicon이 마지막으로 추가될 global_posting 위치 저장
            lexicon_idx = list(global_lexicon.keys()).index(term)
            posting_data = [lexicon_idx, doc_idx, max_tf(freq, max_freq, 0), before_idx]   # 처음 추가되는 lexicon은 before_idx가 None
            global_posting.append(posting_data)
            posting_idx += 1
    
    for i, posting_data in enumerate(global_posting):
        if posting_data[3] is None:
            global_posting[i][3] = -1

    return global_lexicon, global_posting, global_document, dtm


def get_tdm_from_dtm(dtm):
    '''
    # convert to Inverted Document
    # (to Term-Document Matrix from Document-Term Matrix)

    # dictionary 내에 dictionary를 포함하고 있는 구조
        {"term1": {"document1": tf1,
                   "document2": tf2,
                    ...
                  }
         "term2": { ... 
                  }
         ...
        }
    '''
    tdm = defaultdict(lambda: defaultdict(int))
    
    for filename, termlist in dtm.items():   # dtm : [filename][term][frequency]
        # max_freq = max(termlist.values())
        
        for term, freq in termlist.items():
            tdm[term][filename] = freq    # max_tf(freq, max_freq, 0)
            
    return tdm


def tdm2twm(tdm, global_document):
    '''
    Term-Document Matrix로 부터 Term-Weight Matrix로 변환 합니다.
    TWM의 Weight는 TDM의 Frequancy인 max_tf(0, freq, max_freq)와 raw_idf(df, document_count)의 곱 입니다.
    함께 반환되는 DVL(Document Vector Length)은 TWM의 Weight ** 2의 값 입니다.
    '''
    document_count = len(global_document)
    twm = defaultdict(lambda: defaultdict(float))
    dvw = defaultdict(float)    # document vector weight

    for term, tf_list in tdm.items():
        df = len(tf_list)
        # idf = raw_idf(df, document_count)
        idf = smoothig_idf(df, document_count)
        
        for filename, tf in tf_list.items():
            twm[term][filename] = tf * idf       # weight
            dvw[filename][term] = twm[term][filename]  ** 2
        
    return twm, dvw


def evaluate_idf(global_lexicon, global_posting, global_document):
    '''
    idf 값을 산출하여, tf-idf 값을 계산하고,
    global_posting의 posting_data[2] 빈도 부분에 포함하여 반환 합니다.
    '''
    global_lexicon_idf = dict()
    global_document_weight = dict()

    document_count = len(global_document)

    for term, posting_idx in global_lexicon.items():
        df = 0
        old_posting_idx = posting_idx

        while True:    # Posting Nexting: -1 
            if posting_idx == -1:
                break

            df += 1
            posting_data = global_posting[posting_idx]
            posting_idx = posting_data[3]

        # idf = raw_idf(df, document_count)
        idf = smoothig_idf(df, document_count)
        global_lexicon_idf[term] = idf
        posting_idx = old_posting_idx

        #print("{0} / IDF-{1}".format(term, idf))

        while True:
            if posting_idx == -1:
                break

            posting_data = global_posting[posting_idx]

            # tf = posting_data[2]      # 아래 print 문에 사용 시 주석 해제
            # print("    Documents:{0} / TF:{1} / TF-IDF:{2}".format(
            #     global_document[posting_data[1]], tf, global_posting[posting_idx][2]))

            if global_document[posting_data[1]] not in global_document_weight.keys():
                global_document_weight[global_document[posting_data[1]]] = (posting_data[2] * idf) ** 2
            else:
                global_document_weight[global_document[posting_data[1]]] += (posting_data[2] * idf) ** 2

            posting_idx = posting_data[3]   # 다음 주소를 할당

    return global_lexicon_idf, global_document_weight