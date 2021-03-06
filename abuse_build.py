import numpy as np
import pandas as pd
import re
import os
from keras.layers import Dropout
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, Dense, LSTM, GRU, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.text import Tokenizer


#불용어 사전
stop_words = set(stopwords.words('english'))
URL_REGEX = re.compile(r'http\S{7,}')


#CSV 불러오면서 df 정리
def Load_data(directory):
    try:
        data = pd.read_csv(directory)
        data = data.drop_duplicates(['CONTENT'])            #CONTENT 컬럼 중복 DATA 삭제
        data = data.dropna()                                #NULL 제거
        data = data.sample(frac=1).reset_index(drop=True)   #셔플, 인덱스 재배열
        #del data['Unnamed: 0']                              #csv 머지하면 가끔 생기던데 그거 지우기

        return data

    except FileNotFoundError:
        raise FileNotFoundError("INPUT DATA 경로 잘못됨.")

#토크나이징, 정제화, BOW 생성
def Preprocess(data):

    Tokenized = []

    for sentence in data['CONTENT']:
        sentence = sentence.lower()     # 소문자로 변환
        URL = re.search(URL_REGEX, sentence)

        if URL != None:
            URL = URL.group()
            sentence = sentence.replace(URL, "") #URL 제거

        sentence = re.sub(r"[^a-zA-Z ]", " ", sentence)


        tokens = sentence.split(' ')
        tokens = [word for word in tokens if not word in stop_words] # 불용어 제거

        for i in reversed(range(len(tokens))):

            # 길이 1이하인 TOKEN 제거
            if len(tokens[i]) < 2:
                del tokens[i]

            #불용어 처리 이후 남은 None TOKEN 제거
            elif tokens[i] == '':
                del tokens[i]


        Tokenized.append(tokens)

    return Tokenized


#TRAIN, TEST 분리
def Seperate(DATA):

    if len(DATA) > 10:
        #data의 20%를 검증용 testdata, 80%를 학습용 traindata로 분리
        TRAIN_DATA = DATA[int(len(DATA) * 0.2) + 1:]
        TEST_DATA = DATA[:int(len(DATA) * 0.2)]

        #욕설인지 판단하는 'ABUSE' 컬럼 분리
        TRAIN_DATA_FLAG = np.array(TRAIN_DATA['ABUSE'])
        TEST_DATA_FLAG = np.array(TEST_DATA['ABUSE'])

        return TRAIN_DATA, TEST_DATA, TRAIN_DATA_FLAG, TEST_DATA_FLAG
    else:
        raise FileNotFoundError("DATA 부족.")



def Fitting(DATA):
    #BOW에 대해 정수 인덱스 부여
    BOW = Tokenizer()
    BOW.fit_on_texts(DATA)

    threshold = 2  #기준 기준 엄기준
    total_cnt = len(BOW.word_index) # 단어의 수

    rare_cnt = 0    # 등장 빈도수가 threshold보다 작은 단어의 개수를 카운트
    total_freq = 0  # TRAIN_DATA의 전체 단어 빈도수 총 합
    rare_freq = 0   # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

    # 단어와 빈도수의 PAIR를 Key, Value로 받기
    for key, value in BOW.word_counts.items():
        total_freq = total_freq + value

        # 단어의 등장 빈도수가 threshold보다 작으면
        if(value < threshold):
            rare_cnt = rare_cnt + 1
            rare_freq = rare_freq + value

    vocab_size = total_cnt - rare_cnt + 1

    #vocab_size 가 너무 적으면 학습의 의미가 없기에 에러 raise
    if vocab_size < 100:
        raise ValueError("Vocab_size의 크기가 100 이하입니다. Training Input Data를 늘려야 합니다.")

    print('Vocab Size = ',vocab_size)

    BOW = Tokenizer(vocab_size)
    BOW.fit_on_texts(DATA)

    return BOW, vocab_size


#전체 DATA에서 지정된 max_len 보다 짧은 DATA의 비율
def Under_Max(max_len, SERIES):
    cnt = 0
    for s in SERIES:
        if (len(s) <= max_len):
            cnt = cnt + 1

    print('전체 DATA 중 길이가 %s 이하인 DATA의 비율: %s' % (max_len, (cnt / len(SERIES)) * 100))


#BOW에 fit시킨 tokenizer 피클 파일로 저장
def Pickling(TOKENIZER):

    import pickle

    with open('Abuse_Tokenizer.pickle', 'wb') as handle:
        pickle.dump(TOKENIZER, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("saving BOW to Abuse_Tokenizer.pickle")

#BOW 정수 인덱싱
def Indexing(DATA, BOW):

    DATA = BOW.texts_to_sequences(DATA)

    return DATA

#Input의 크기를 맞춰주기 위해 zero-padding
def Padding(DATA, max_len):

    DATA = pad_sequences(DATA, maxlen=max_len)

    return DATA

#모델 빌드
def Build_Model(vocab_size):
    model = Sequential()

    model.add(Embedding(vocab_size, 128))   #임베딩 벡터의 차원 100
    model.add(Dropout(0.2))                 #과소적합 방지용 Dropout층
    model.add(LSTM(128))                    #LSTM 모델
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])

    return model

#모델 학습 및 저장
def Train_Model(MODEL, TRAIN, TRAIN_FLAG, EPOCH, BATCH, MODEL_H5): #output must be ~~~.h5 format

    #Validation loss 가 3회 증가하면 학습 종료
    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=3)

    #학습하면서 이전 모델보다 ACC가 높을때만 .h5파일로 저장
    mc = ModelCheckpoint(MODEL_H5, monitor='val_acc', mode='max', verbose=1, save_best_only=True)

    #학습
    history = MODEL.fit(TRAIN, TRAIN_FLAG, epochs=EPOCH, callbacks=[es, mc], batch_size=BATCH, validation_split=0.2, shuffle=True)


#모델 평가
def Evaluate(MODEL_H5, TEST, TEST_FLAG):
    MODEL = load_model(MODEL_H5)
    print("\n MODEL ACC: %.4f" % (MODEL.evaluate(TEST, TEST_FLAG)[1]))


def Main():
    #Input CSV 불러오기
    DATA = Load_data("/dataset/ADATA.csv")

    #학습, 검증 DATA 분리
    TRAIN_DATA, TEST_DATA, TRAIN_DATA_FLAG, TEST_DATA_FLAG = Seperate(DATA)

    #분리된 데이터 전처리(갑자기 든 생각 : 전처리 하고 분리하면 코드 한 줄 줄어듦)
    TRAIN_DATA = Preprocess(TRAIN_DATA)
    TEST_DATA = Preprocess(TEST_DATA)

    #keras.tokenizer에 fit, BOW 생성
    BOW, vocab_size = Fitting(TRAIN_DATA)

    #BOW 저장
    Pickling(BOW)

    #정수 인덱싱
    TRAIN_DATA = Indexing(TRAIN_DATA, BOW)
    TEST_DATA = Indexing(TEST_DATA, BOW)

    #Input의 최대 크기 지정
    max_len = 20

    #print('TRAIN DATA의 최대 길이 :',max(len(l) for l in TRAIN_DATA_BOW))
    #print('TRAIN DATA의 평균 길이 :',sum(map(len, TRAIN_DATA_BOW))/len(TRAIN_DATA_BOW))

    #max_len의 크기에 맞춰 제로패딩
    TRAIN_DATA = Padding(TRAIN_DATA, max_len)
    TEST_DATA = Padding(TEST_DATA, max_len)

    #빌드
    MODEL = Build_Model(vocab_size)

    #학습 및 저장
    Train_Model(MODEL, TRAIN_DATA, TRAIN_DATA_FLAG, 10, 1000, "Abuse_Detect.h5")

    #검증
    Evaluate('Abuse_Detect.h5', TEST_DATA, TEST_DATA_FLAG)

Main()
