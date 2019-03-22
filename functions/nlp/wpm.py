'''
WPM : 하나의 단어를 내부 단어(Subword Unit)들로 분리하는 단어 분리 모델

각 음절 <- whitespace(' '), 공백이 나오면 '_' 추가
각 단어의 끝에 <= </w> 추가

데이터: 각 단어의 빈도

1. 음절을 쪼개기
2. 패턴을 만들기 (n=2)
3. 빈도가 가장 높은 best case 1개 찾기
4. 병합
5. 2번 부터 반복(n)
'''
import re
from collections import defaultdict


def split_terms(term):
    '''
    모든 문자를 공백으로 분리, 단어의 시작에는 <w> 추가, 단어의 끝에는 </w> 추가
    원래 공백은 "_"로 대체, 원래 "_"를 구분하기 위해 원래 "_"를 "__"(두개)로 대체

    예) split_terms("lower low_est") 실행 결과:
        '<w> l o w e r </w> _ <w> l o w __ e s t </w>' 
    '''
    termLists = term.split()
    result = []
    for termList in termLists:
        result.append((" ".join(['<w>']+list(termList)+['</w>'])).replace("_", "__"))
    return " _ ".join(result)


def find_ngram(tokens, n=2):
    '''
    공백으로 분리된 tokens을 받아서, 지정한 ngram으로 분리한 결과를 반환 합니다.

    n => ngram (몇 개씩 묶을지 지정)
    tokens => key: 공백으로 분리된 문자(split_terms), value: 해당 문자가 나타난 횟수
    
    예)
    tokens = {
        split_terms("low"):5,
        split_terms("lowest"):2,
        split_terms("newer"):6,
        split_terms("wider"):3
    }

    find_ngram(tokens, 3) 실행 결과:
    defaultdict(int,
            {('<w>', 'l', 'o'): 7,
             ('l', 'o', 'w'): 7,
             ('o', 'w', '</w>'): 5,
             ('o', 'w', 'e'): 2,
             ('w', 'e', 's'): 2,
             ('e', 's', 't'): 2,
             ('s', 't', '</w>'): 2,
             ('<w>', 'n', 'e'): 6,
             ('n', 'e', 'w'): 6,
             ('e', 'w', 'e'): 6,
             ('w', 'e', 'r'): 6,
             ('e', 'r', '</w>'): 9,
             ('<w>', 'w', 'i'): 3,
             ('w', 'i', 'd'): 3,
             ('i', 'd', 'e'): 3,
             ('d', 'e', 'r'): 3})
    '''
    if n < 2:
        print("n 값은 2 이상 이어야 합니다. (일반적으로, 2~4의 값 선택)")
        return None
    
    result = defaultdict(int)
    
    for k, v in tokens.items():
        term = k.split()
        
        for i in range(len(term) - n + 1):
            ngram = tuple(term[i:i+n])
            # n=2 : (<w>, l), (l, o), (o, w), (w, </w>)
            # n=3 : (<w>, l, o), (l, o, w), (o, w, </w>)
            
            if ngram in result.keys():
                result[ngram] += v
            else:
                result[ngram] = v
    return result


def merge_ngram(maxkey, tokens):
    '''
    tokens에서 maxkey를 찾아서, 공백을 없애고 하나의 문자처럼 합친 후 tokens을 반환 합니다.

    예)
    tokens = {
        split_terms("low"):5,
        split_terms("lowest"):2,
        split_terms("newer"):6,
        split_terms("wider"):3
    }

    for i in range(5):
        pattern = find_ngram(tokens, 3)

        maxkey = max(pattern, key=pattern.get)

        tokens = merge_ngram(maxkey, tokens)

        print(maxkey)
        print(tokens) 
    
    실행결과:
        ('e', 'r', '</w>')
        defaultdict(<class 'int'>, {'<w> l o w </w>': 5, '<w> l o w e s t </w>': 2, '<w> n e w er</w>': 6, '<w> w i d er</w>': 3})
        ('<w>', 'l', 'o')
        defaultdict(<class 'int'>, {'<w>lo w </w>': 5, '<w>lo w e s t </w>': 2, '<w> n e w er</w>': 6, '<w> w i d er</w>': 3})
        ('<w>', 'n', 'e')
        defaultdict(<class 'int'>, {'<w>lo w </w>': 5, '<w>lo w e s t </w>': 2, '<w>ne w er</w>': 6, '<w> w i d er</w>': 3})
        ('<w>ne', 'w', 'er</w>')
        defaultdict(<class 'int'>, {'<w>lo w </w>': 5, '<w>lo w e s t </w>': 2, '<w>newer</w>': 6, '<w> w i d er</w>': 3})
        ('<w>lo', 'w', '</w>')
        defaultdict(<class 'int'>, {'<w>low</w>': 5, '<w>lo w e s t </w>': 2, '<w>newer</w>': 6, '<w> w i d er</w>': 3})
    '''
    result = defaultdict(int)
    
    token = " ".join(maxkey)
    
    # "(?!=\S)" : whitespace가 아닌 것 
    pattern = re.compile(r"(?!=\S)" + token + "(?!\S)") 
    
    for k, v in tokens.items():
        new = pattern.sub("".join(maxkey), k)
        result[new] = v
        
    return result