import flask_reqparse as reqparse
from flask import Flask
from tensorflow.keras.models import load_model
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re, pickle
import spacy

SPACY_LOAD = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')

stop_words = set(stopwords.words('english'))


with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

loaded_model = load_model('best_model.h5')


loaded_model.summary()

app = Flask(__name__)

@app.route('/')
def mainpage():
    return 'Hi minsoo'


@app.route('/predict', methods=['POST'])
def abuse_predict():
    print('prediction api called.')
    parser = reqparse.RequestParser()
    parser.add_argument('content')#json key 추가

    sentence = parser.parse_args()['content']

    sentence = sentence.replace("Org Name:", "")
    original = sentence

    print(sentence)


    sentence = sentence.lower()  # 소문자로 변환
    tokens = sentence.split(' ')  # 공백 기준 스플릿
    token_score = []

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

    print(tokens)

    encoded = tokenizer.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, 20) # 패딩
    total_score = float(loaded_model.predict(pad_new)) # 예측

    for i in range(len(tokens)):
        encoded = tokenizer.texts_to_sequences([tokens[i]])  # 정수 인코딩
        pad_new = pad_sequences(encoded, 20)  # 패딩
        score = float(loaded_model.predict(pad_new))
        score = str(round(score * 100, 2))# 예측
        token_score.append(score)


    if(total_score > 0.5):
        result = {"spamResult": "<result><totalscore>" + str(round(total_score * 100, 2)) + "</totalscore><totallevel>ABUSIVE</totallevel><suspicion><type>nlp</type><score>" + str(token_score) + "</score><level>ABUSIVE</level><token>" + str(tokens) + "></token></suspicion></result>"}

    else:
        result = {"spamResult": "<result><totalscore>" + str(round(total_score * 100, 2)) + "</totalscore><totallevel>NON-ABUSIVE</totallevel><suspicion><type>nlp</type><score>" + str(token_score) + "</score><level>NON-ABUSIVE</level><token>" + str(tokens) + "</token></suspicion></result>"}

    print(result)
    return result, 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
