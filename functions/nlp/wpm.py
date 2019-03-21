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
def splitTerms(term):
    pass

def findNgram(tokens, n=2):
    pass

def mergeNgram(maxKey, data):
    pass