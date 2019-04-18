'''
본 코드는 IPA 인공지능(언어지능) 교육 과정의 프로젝트 산출물 입니다.
Information Retrieval(정보검색) 관련 함수를 정의 합니다.

버지니아대학의 "CS 4501: Information Retrieval" 과정을 참고하여 색인, 질의 관련 함수를 구현 했습니다.
버지니아대학 강의 사이트 : http://www.cs.virginia.edu/~hw5x/Course/IR2015/_site/lectures/
'''
import os
import re
from string import punctuation
from collections import defaultdict
from math import log10
import pickle

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

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
    return np.where(freq > 0, freq, 0)


def norm_tf(freq, total_freq=1):
    '''
    return: freq / total_freq
    '''
    if total_freq > 0:
        return np.where(freq > 0, freq, 0) / total_freq
    else:
        return None


def log_tf(freq):
    '''
    return: 1+log10(freq), if freq > 0
            0, otherwise
    '''
    # if freq > 0:
    #     return 1+log10(freq)
    # else:
    #     return 0
    return np.log10(np.where(freq > 0, freq, 1))


def max_tf(freq, max_freq, alpha=0.5):
    '''
    alpha(0<alpha<1)와 1 사이의 값으로 정규화 됨 (double normalization K)
    return: alpha + (1-alpha) * (freq / max_freq)
    '''
    if max_freq > 0:
        return alpha + (1-alpha) * (np.where(freq > 0, freq, 0) / max_freq)
    else:
        return None


def raw_idf(df, n):
    '''
    # 일반적인 IDF 정의
    return: log10(n/df)

    df: document frequency
    n: document count
    '''
    if n > 0:
        return np.log10(n / np.where(df > 0, df, n))
    else:
        return None


def smoothig_idf(df, n):
    '''
    return: log10((n+1)/df)

    df: document frequency
    n: document count
    '''
    if n > 0:
        return np.log10((n+1) / np.where(df > 0, df, n+1))
    else:
        return None


def probability_idf(df, n):
    '''
    return: log10((n-df)/df)    # N - df가 0이면 0을 return 하도록 조건 검사

    df: document frequency
    n: document count
    '''
    if n > 0 or max(df) > n:
        return np.log10(np.where(n-df != 0, ((n-df) / np.where(df > 0, df, (n-df))), 1))
    else:
        return None


def get_lexicon(corpus=kobill):
    '''
    corpus 데이터를 인수로 받아서, 공백으로 분리한 lexicon을 numpy array 형태로 반환 합니다.
    인수 corpus에는 corpus 객체를 전달 합니다.
    default로 konlpy 패키지의 kobill(의안) 자료를 lexicon으로 반환 합니다.

    사용예)
        from konlpy.corpus import kolaw
        from functions.info_retrieval import get_lexicon

        lexicon = get_lexicon(corpus=kolaw)
    '''
    lexicon = np.array(list())
    for document in corpus.fileids():
        content = corpus.open(document).read()
        lexicon = np.append(lexicon, np.array(content.split()))
                
    return lexicon


def get_tfidf_from_konlpy(corpus=kobill, k_morpheme=Kkma):
    '''
    한국어 형태소 분석기를 이용(default로 Kkma 사용)해서, tf-idf를 산출 합니다.
    sklearn의 TfidfVectorizer를 이용 합니다.

    return: document list, vectorizer object, tfidf array

    vectorizer object에는 lexicon list가 포함되어 있습니다.
    아래와 같이 사용할 수 있습니다.
        lexicon_list = np.array(vectorizer.get_feature_names())
        lexicon_dict = vectorizer.vocabulary_
    '''
    morpheme = k_morpheme().morphs

    documents = np.array(corpus.fileids())
    contents = np.array(list())

    for document in documents:
        contents = np.append(contents, [corpus.open(document).read()])
    
    vectorizer = TfidfVectorizer(tokenizer=morpheme)
    tfidf = vectorizer.fit_transform(contents)

    return documents, vectorizer, tfidf


def get_tfidf_from_nltk(corpus=gutenberg, e_tokenize=None):
    '''
    nltk에서 제공하는 tokenizer를 이용(default로 work_tokenize를 사용)해서, tf-idf를 산출 합니다.
    sklearn의 TfidfVectorizer를 이용 합니다.

    return: document list, vectorizer object, tfidf array

    vectorizer object에는 lexicon list가 포함되어 있습니다.
    아래와 같이 사용할 수 있습니다.
        lexicon_list = np.array(vectorizer.get_feature_names())
        lexicon_dict = vectorizer.vocabulary_
    '''
    documents = np.array(corpus.fileids())
    contents = np.array(list())

    for document in documents:
        contents = np.append(contents, [corpus.open(document).read()])
    
    vectorizer = TfidfVectorizer(tokenizer=e_tokenize, stop_words="english")
    tfidf = vectorizer.fit_transform(contents)

    return documents, vectorizer, tfidf


def get_remove_pattern():
    '''
    corpus에서 제거할 문자의 정규표현식이 dictionary로 작성 되어 있습니다.

    사용예)
        corpus = get_remove_pattern()["email"].sub(" ", corpus)
    '''
    patterns = {}
    patterns["email"] = re.compile(r"(\w+@[a-zA-Z0-9\-\_]{3,}(\.[a-zA-Z]{2,})+)")
    patterns["url"] = re.compile(r"(https?:\/\/)?([\w\d-]{3,}(\.[a-zA-Z]{2,})+)")
    patterns["max_length"] = re.compile(r"(\b[\w\d가-힣]{8,}\b)")
    patterns["numeric_length"] = re.compile(r"(\b(\d{1}|\d{5,})\b)")
    patterns["punctuation"] = re.compile(r"([%s]{2,})" % re.escape(punctuation))
    patterns["invalid_korean"] = re.compile(r"([ㄱ-ㅎㅏ-ㅣ]+)")
    patterns["whitespace"] = re.compile(r"((\s{2,})+|((\\n){2,})+)")
    patterns["non_word"] = re.compile(r"([^\w\d가-힣])")

    return patterns


def clean_collection(collection):
    '''
    collection의 content에 포함된 email, url, 8자 이상의 글자, 숫자(1글자 또는 5자 이상), 
    Non_Word, white space 등을 제거하고 Cleaned collection을 반환 합니다.

    collection은 list [document이름, content]들의 리스트인 2차원 ndarray 입니다.
    '''
    cleaned_collection = list()

    for filename, content in collection:
        cleaned_content = get_remove_pattern()["email"].sub(" ", content)
        cleaned_content = get_remove_pattern()["url"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["max_length"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["numeric_length"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["punctuation"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["invalid_korean"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["whitespace"].sub(" ", cleaned_content)
        cleaned_content = get_remove_pattern()["non_word"].sub(" ", cleaned_content)
        cleaned_collection.append([filename, cleaned_content])

    return cleaned_collection


def extend_lexicon(corpus):
    '''
    collection의 document별 content(전처리 된 content)를 받아서 token의 수를 늘려서 lexicon을 반환 합니다.
        --> token = 어절 + 형태소 + 명사 + 바이그램(음절)
    '''
    kkma = Kkma()
    extended_lexicon = np.array(list())

    term_list = np.array([term for term in np.array(corpus.split()) if len(term) > 1])
    pos_list = np.array([morphs for morphs in np.array(kkma.morphs(corpus)) if len(morphs) > 1])
    noun_list = np.array([noun for noun in np.array(kkma.nouns(corpus)) if len(noun) > 1])
    ngram_list = np.array([_ for token in term_list for _ in ngram.ngramUmjeol(token)])

    extended_lexicon = np.append(extended_lexicon, term_list)
    extended_lexicon = np.append(extended_lexicon, pos_list)
    extended_lexicon = np.append(extended_lexicon, noun_list)
    extended_lexicon = np.append(extended_lexicon, ngram_list)

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
    '''
    global_lexicon = dict()
    global_document = list()
    global_posting = list()
    dtm = defaultdict(lambda: defaultdict(int))
    dtm_dict = dict()
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

    # defaultdict를 pickle로 저장 가능한 dict로 변환
    for doc, tf in dtm.items():
        dtm_dict[doc] = tf
    
    return global_lexicon, global_posting, global_document, dtm_dict


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
    tdm_dict = dict()
    
    for filename, termlist in dtm.items():   # dtm : [filename][term][frequency]
        # max_freq = max(termlist.values())
        
        for term, freq in termlist.items():
            tdm[term][filename] = freq    # max_tf(freq, max_freq, 0)
            
    # defaultdict를 pickle로 저장 가능한 dict로 변환
    for term, file_freq in tdm.items():
        tdm_dict[term] = file_freq
    
    return tdm_dict


def tdm2twm(tdm, global_document):
    '''
    Term-Document Matrix로 부터 Term-Weight Matrix로 변환 합니다.
    TWM의 Weight는 TDM의 Frequancy인 max_tf(0, freq, max_freq)와 raw_idf(df, document_count)의 곱 입니다.
    함께 반환되는 DVL(Document Vector Length)은 TWM의 Weight ** 2의 값 입니다.
    '''
    document_count = len(global_document)
    twm = defaultdict(lambda: defaultdict(float))
    dtw = defaultdict(lambda: defaultdict(float))    # document vector weight
    twm_dict = dict()
    dtw_dict = dict()

    for term, tf_list in tdm.items():
        df = len(tf_list)
        # idf = raw_idf(df, document_count)
        idf = smoothig_idf(df, document_count)
        
        for filename, tf in tf_list.items():
            twm[term][filename] = tf * idf       # weight
            dtw[filename][term] = twm[term][filename]  ** 2
    
    # defaultdict를 pickle로 저장 가능한 dict로 변환
    for term, file_weight in twm.items():
        twm_dict[term] = file_weight
    
    for filename, term_weight in dtw.items():
        dtw_dict[filename] = term_weight

    return twm_dict, dtw_dict


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


def query_index(query):
    '''
    query에서 형태소를 분리하여, token과 frequency를 dictionary로 반환 합니다.
    query : 문자열
    query_repr : {"token": frequency}
    '''
    kkma = Kkma().morphs
    query_repr = defaultdict(int)

    for token in query.split():
        for morpheme in kkma(token):
            if len(morpheme) > 1:
                query_repr[morpheme] += 1
    
    return query_repr


def eval_query_weight(query_repr, global_lexicon_idf):
    '''
    query에서 추출한 형태소들의 TF-IDF 값을 반환 합니다.
    query_weight : {"token": tf-idf}
    '''
    max_freq = max(query_repr.values())
    query_weight = defaultdict(float)

    for token, freq in query_repr.items():
        if token in global_lexicon_idf.keys():
            tf = max_tf(freq, max_freq, 0.5)
            idf = global_lexicon_idf[token]
            query_weight[token] = tf * idf
    
    return query_weight


def euclidian(x, y):
    '''
    euclidian distance를 산출 합니다.
    x: query에서 추출한 token의 query_weight
    y: document에서 추출한 token의 weight(tfidf)
    '''
    return (x-y) **2


def inner_product(x, y):    # x는 query_weight, y는 document_weight
    '''
    Cosine similarity를 산출 합니다.
    x: query에서 추출한 token의 query_weight
    y: document에서 추출한 token의 weight(tfidf)
    '''
    return x * y


def candidate_list_by_euclidian(query_weight, global_lexicon, twm):
    candidate_list = dict()

    for index_term, _ in global_lexicon.items():
        query_tfidf = 0

        if index_term in query_weight.keys():
            query_tfidf = query_weight[index_term]

        for filename, document_weight in twm[index_term].items():
            if filename not in candidate_list.keys():
                candidate_list[filename] = euclidian(query_tfidf, document_weight)
            else:
                candidate_list[filename] += euclidian(query_tfidf, document_weight)
    
    return candidate_list


def candidate_list_by_cosine(query_weight, global_lexicon, global_posting, global_document, global_document_weight):
    candidate_list = dict()

    for index_term, q_weight in query_weight.items():
        if index_term in global_lexicon.keys():
            posting_idx = global_lexicon[index_term]

            while True:
                if posting_idx == -1:
                    break

                posting_data = global_posting[posting_idx]
                posting_idx = posting_data[3]
                document_weight = posting_data[2]

                if global_document[posting_data[1]] not in candidate_list.keys():
                    candidate_list[global_document[posting_data[1]]] = inner_product(q_weight, document_weight)
                else:
                    candidate_list[global_document[posting_data[1]]] += inner_product(q_weight, document_weight)

    for document_idx, _ in candidate_list.items():
        candidate_list[document_idx] /= global_document_weight[document_idx]

    return candidate_list


def euclidian_sort(candidate_list):
    '''
    euclidian distance에 대한 오름차순 정렬
    '''
    result_list = sorted(candidate_list.items(), key=lambda x:x[1])
    return result_list


def cosine_sort(candidate_list):
    '''
    Cosine similarity에 대한 내림차순 정렬
    '''
    result_list = sorted(candidate_list.items(), key=lambda x:x[1], reverse=True)
    return result_list


def result_print(query, result_list, global_document, collection, count=3):
    print("query: ", query)

    if count > len(result_list):
        count = len(result_list)

    for i, (document, distance) in enumerate(result_list[:count]):
        print("순위:{0} / 문서:{1} / 유사도:{2}".format((i+1), document, distance))
        print("   document:{0}".format(collection[global_document.index(document)]))
    
    return None


def save_pickle(pickle_object, save_dir="../naver_news/pickle/"):
    for pickle_name, pickle_obj in pickle_object.items():
        file_path = os.path.join(save_dir, pickle_name + ".pickle")
        with open(file_path, "wb") as f:
            pickle.dump(pickle_obj, f)
            print("{0} is saved.".format(file_path))