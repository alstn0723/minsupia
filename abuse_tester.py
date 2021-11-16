from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from tensorflow.keras.models import load_model
import pickle, re

URL_REGEX = re.compile(r'http\S{7,}')


#NLTK 불용어 사전
stop_words = set(stopwords.words('english'))
#모델 로드
def Load_Model(MODEL_H5, BOW_PICKLE):

    try:
        with open(BOW_PICKLE, 'rb') as handle:
            BOW = pickle.load(handle)

        MODEL = load_model(MODEL_H5)

        return MODEL, BOW
    except FileNotFoundError:
        raise FileNotFoundError("Pickle 파일 경로 잘못됨.")
    except IOError:
        raise FileNotFoundError("h5 파일 경로 잘못됨.")


MODEL, BOW = Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')


def Preprocess_Predict(sentence):

    sentence = sentence.lower()     # 소문자로 변환
    URL = re.search(URL_REGEX, sentence)

    if URL != None:
        URL = URL.group()
        sentence = sentence.replace(URL, "")  # URL 제거

    sentence = re.sub(r"[^a-zA-Z ]", " ", sentence)

    tokens = sentence.split(' ')
    tokens = [word for word in tokens if not word in stop_words]  # 불용어 제거

    for i in reversed(range(len(tokens))):
        # 길이 1인 찌꺼기 제거
        if len(tokens[i]) < 2:
            del tokens[i]

        # 불용어 처리 이후 남은 null 제거
        elif tokens[i] == '':
            del tokens[i]

    return tokens


def ACC_Check(sentence, MODEL, BOW):

    tokens = Preprocess_Predict(sentence)
    token_score = []

    encoded = BOW.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, 20) # 패딩
    total_score = float(MODEL.predict(pad_new)) # 예측

    for i in range(len(tokens)):
        encoded = BOW.texts_to_sequences([tokens[i]])  # 정수 인코딩
        pad_new = pad_sequences(encoded, 20)  # 패딩
        score = float(MODEL.predict(pad_new))
        score = str(round(score * 100, 2))# 예측
        token_score.append(score)

    total_score = round(total_score * 100, 4)
    return sentence, total_score, tokens, token_score


'''
    if (total_score > 0):
        print("DATA total score : {0} ".format(round(total_score * 100, 4)))
        print(sentence)
        for i in range(len(tokens)):
            print("{0}  ==>  {1}".format(tokens[i], token_score[i]))
'''
