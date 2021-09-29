import numpy as np
import pandas as pd
import re, collections
from nltk.corpus import stopwords
#from nltk.tag import pos_tag
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, Dense, LSTM, GRU, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
import tensorflow as tf

#불용어 사전
stop_words = set(stopwords.words('english'))
'''
#교정 사전 내 단어 추출
def words(text): return re.findall('[a-z]+', text.lower())

#교정 사전 모델
def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

dic = open('big.txt').read()
NWORDS = train(words(dic))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

#편집거리 1 기준 candidate
def edits_dtc1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

#편집거리 2기준 candidate
def edits_dtc2(word):
    return set(e2 for e1 in edits_dtc1(word) for e2 in edits_dtc1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits_dtc1(word)) or edits_dtc2(word) or [word]
    return max(candidates, key=NWORDS.get)




def sweep(list):
    for i in range(len(list)):
        #delete newline
        list[i] = list[i].replace('\n', ' ')

        #lower case
        list[i] = list[i].lower()

        #tokenize
        list[i] = list[i].split(' ')

        #delete null
        list[i] = [v for v in list[i] if v]

    return list


#ex = sweep(pd2array)
#print(len(ex))

#길이가 2 이하인 찌꺼기 삭제
def deletesmall(list):
    for i in reversed(range(len(list))):
        for j in reversed(range(len(list[i]))):
            if (len(list[i][j]) <= 2) :
                del list[i][j]

    for i in reversed(range(len(list))):
        if (list[i] == []):
            del list[i]

    return list
'''

email_regex = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
#date_regex = re.compile()


#find a listed mms which include e-mail
def emailfind(list):
    emailhere = []

    for i in range(len(list)):
        for j in range(len(list[i])):
            if (None!= email_regex.match(list[i][j])):
                print('email here.')
                emailhere.append(list[i])
            else:
                print('No email!')
    return emailhere

def loadmerged(directory):
    data = pd.read_csv(directory)
    data = data.dropna()#nan 한번 더 체크
    data = data.sample(frac=1).reset_index(drop=True)#셔플, 인덱스 재배열


    return data

def Tokenize(data):

    BoW = []

    for sentence in data['CONTENT']:
        sentence = sentence.lower()  # 소문자로 변환
        tokens = sentence.split(' ')  # 공백 기준 스플릿
        for i in reversed(range(len(tokens))):
            if '@' in tokens[i]:
                del tokens[i]
            elif '&' in tokens[i]:
                del tokens[i]
            elif 'http' in tokens[i]:
                del tokens[i]
            elif '#' in tokens[i]:
                del tokens[i]
            else:
                tokens[i] = re.sub(r"[^a-zA-Z ]", " ", tokens[i])

        tokens = ' '.join(tokens)
        tokens = tokens.split(' ')
        tokens = [word for word in tokens if not word in stop_words] # 불용어 제거

        for i in reversed(range(len(tokens))):
            #불용어 처리 이후 남은 null 제거
            if tokens[i] == '': del tokens[i]
            #길이 1인 찌꺼기 제거
            elif len(tokens[i]) < 2: del tokens[i]

        BoW.append(tokens)

    return BoW

data = loadmerged("final.csv")
data.drop_duplicates(['CONTENT'])
del data['Unnamed: 0']
data = data.dropna()
data = data.sample(frac=1).reset_index(drop=True)
#data2 = data
#data의 20%를 검증용 testdata, 80%를 학습용 traindata로 분리
testdata = data[:int(len(data) * 0.2)]
data = data[int(len(data) * 0.2) + 1:]

bow = Tokenize(data)
testbow = Tokenize(testdata)

#욕설인지 판단하는 'ABUSE' 컬럼 분리
data_abuse = np.array(data['ABUSE'])
testdata_abuse = np.array(testdata['ABUSE'])

#BagofWords에 대해 정수 인덱스 부여
tokenizer = Tokenizer()
tokenizer.fit_on_texts(bow)

threshold = 3
total_cnt = len(tokenizer.word_index) # 단어의 수
print(total_cnt)
rare_cnt = 0 # 등장 빈도수가 threshold보다 작은 단어의 개수를 카운트
total_freq = 0 # 훈련 데이터의 전체 단어 빈도수 총 합
rare_freq = 0 # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

# 단어와 빈도수의 쌍(pair)을 key와 value로 받는다.
for key, value in tokenizer.word_counts.items():
    total_freq = total_freq + value

    # 단어의 등장 빈도수가 threshold보다 작으면
    if(value < threshold):
        rare_cnt = rare_cnt + 1
        rare_freq = rare_freq + value

vocab_size = total_cnt - rare_cnt + 1
print('단어 집합의 크기 :',vocab_size)
tokenizer = Tokenizer(vocab_size)
tokenizer.fit_on_texts(bow)

import pickle

with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("피클 잘 담궈짐")



print(type(tokenizer))
bow = tokenizer.texts_to_sequences(bow)
testbow = tokenizer.texts_to_sequences(testbow)

print(len(bow), len(data_abuse))
print(len(testbow), len(testdata_abuse))

print(len(bow))
print(len(data_abuse))

print('텍스트의 최대 길이 :',max(len(l) for l in bow))
print('텍스트의 평균 길이 :',sum(map(len, bow))/len(bow))

def below_threshold_len(max_len, nested_list):
  cnt = 0
  for s in nested_list:
    if(len(s) <= max_len):
        cnt = cnt + 1
  print('전체 샘플 중 길이가 %s 이하인 샘플의 비율: %s'%(max_len, (cnt / len(nested_list))*100))
#data의 96%가 12보다 작고 , 99.9%가 15보다 작음.
max_len = 12

bow = pad_sequences(bow, maxlen = max_len)
testbow = pad_sequences(testbow, maxlen = max_len)

model = Sequential()
#임베딩 벡터의 차원 100
model.add(Embedding(vocab_size, 100))
model.add(LSTM(128))
model.add(Dense(1, activation='sigmoid'))

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)
mc = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])
history = model.fit(bow, data_abuse, epochs=5, callbacks=[es, mc], batch_size=2000, validation_split=0.2, shuffle=True)

loaded_model = load_model('best_model.h5')


print("\n 테스트 정확도: %.4f" % (loaded_model.evaluate(testbow, testdata_abuse)[1]))



def sentiment_predict(sentence,yok,noyok):

    sentence = sentence.lower()  # 소문자로 변환
    tokens = sentence.split(' ')  # 공백 기준 스플릿
    for i in reversed(range(len(tokens))):
        if '@' in tokens[i]:
            del tokens[i]
        elif '&' in tokens[i]:
            del tokens[i]
        elif 'http' in tokens[i]:
            del tokens[i]
        elif '#' in tokens[i]:
            del tokens[i]
        else:
            tokens[i] = re.sub(r"[^a-zA-Z ]", "", tokens[i])

    tokens = ' '.join(tokens)
    tokens = tokens.split(' ')

    print(tokens[i])

    tokens = [word for word in tokens if not word in stop_words]  # 불용어 제거

    for i in reversed(range(len(tokens))):
        # 불용어 처리 이후 남은 null 제거
        if tokens[i] == '':
            del tokens[i]
        # 길이 1인 찌꺼기 제거
        elif len(tokens[i]) < 2:
            del tokens[i]

    print(tokens)

    encoded = tokenizer.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, maxlen = max_len) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측

    if(score > 0.5):
        print("{:.2f}% 확률로 욕설 포함.\n".format(score * 100))
        yok += 1
    else:
        print("{:.2f}% 확률로 욕설 미포함.\n".format((1 - score) * 100))
        noyok += 1

    return yok,noyok


def loadcsv(directory):
    data = pd.read_csv(directory)
    data.drop_duplicates(subset=['CONTENT'], inplace=True)
    data = data['CONTENT']
    data.dropna(inplace=True)
    data = data.reset_index(drop=True)

    print("CSV file loaded.")

    return data
'''
valid = loadcsv("steelo.csv")
valid2 = pd.read_csv("test.csv")
valid2 = valid2['text']
credit = 0

for i in range(10000):
    yok, noyok = sentiment_predict(valid2[i],0,0)
    credit += yok

print(credit)
'''
sentiment_predict("Hi, my name is minsu kim. I'm payment is past due. ",0,0)
sentiment_predict("call 010-2033-2617 or reply by text now.",0,0)
sentiment_predict("what's up bro? Are you dissatisfied with me?",0,0)
sentiment_predict("Shut up bitch. I hate to hear your voice.",0,0)
sentiment_predict("shut the fuck up! Son of a bitch",0,0)
sentiment_predict("You really fucked up this time.",0,0)
sentiment_predict("crime shows  buddy  snuggles   the perfect sunday night  fuck          ",0,0)
sentiment_predict("is this right? mr james?",0,0)
sentiment_predict(" live  the first presidential debate starts now",0,0)
sentiment_predict("some pretty strange things are happening to",0,0)
sentiment_predict("                good luck getting this song out of your head today",0,0)
sentiment_predict("hello this is trumpia. may i help your service?",0,0)
