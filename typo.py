import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

#단어 사전 dictionary 생성(json format)
WORDS = Counter(words(open('norvig.txt').read()))

#correction의 max에서 쓸 key
def Probability(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

#교정
def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=Probability)

#후보군 생성
def candidates(word):
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

#사전에 등장하는 단어 집합
def known(words):
    return set(w for w in words if w in WORDS)

#편집거리 1 교정
def edits1(word):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

#편집거리 2 교정
def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
