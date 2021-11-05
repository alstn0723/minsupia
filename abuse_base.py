from tensorflow.keras.models import load_model
from nltk.corpus import stopwords
import re, pickle

#NLTK 불용어 사전
stop_words = set(stopwords.words('english'))

#모델 로드
def Load_Model(MODEL_H5, BOW_PICKLE):

    #
    with open(BOW_PICKLE, 'rb') as handle:
        BOW = pickle.load(handle)

    MODEL = load_model(MODEL_H5)

    return MODEL, BOW



def Preprocess_Predict(sentence):

    sentence = sentence.lower()     # 소문자로 변환
    tokens = sentence.split(' ')    # 공백 기준 스플릿


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
    tokens = [word for word in tokens if not word in stop_words]  # 불용어 제거

    for i in reversed(range(len(tokens))):

        # 불용어 처리 이후 남은 null 제거
        if tokens[i] == '':
            del tokens[i]

        # 길이 1인 찌꺼기 제거
        elif len(tokens[i]) < 2:
            del tokens[i]

    return tokens




