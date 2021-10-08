import flask_reqparse as reqparse
from flask import Flask
from tensorflow.keras.models import load_model
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re, pickle



stop_words = set(stopwords.words('english'))
loaded_model = load_model('best_model.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


app = Flask(__name__)

@app.route('/')
def mainpage():
    return 'Hi minsoo'


@app.route('/predict/', methods=['POST'])
def abuse_predict():
    print('prediction api called.')
    parser = reqparse.RequestParser()
    parser.add_argument('content')#json key 추가

    sentence = parser.parse_args()['content']
    print(sentence)

    original = sentence

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

    tokens = [word for word in tokens if not word in stop_words]  # 불용어 제거

    for i in reversed(range(len(tokens))):
        # 불용어 처리 이후 남은 null 제거
        if tokens[i] == '':
            del tokens[i]
        # 길이 1인 찌꺼기 제거
        elif len(tokens[i]) < 3:
            del tokens[i]

    print(tokens)

    encoded = tokenizer.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, 12) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측

    if(score > 0.5):
        result = {"spamResult": "<result><totalscore>" + str(round(score * 100, 2)) + "</totalscore><totallevel>ABUSIVE</totallevel><suspicion><type>heuristic</type><score>" + str(round(score * 100, 2)) + "</score><level>ABUSIVE</level><token><![CDATA[" + original + "]]></token></suspicion></result>"}

    else:
        result = {"spamResult": "<result><totalscore>" + str(round(score * 100, 2)) + "</totalscore><totallevel>NON-ABUSIVE</totallevel><suspicion><type>heuristic</type><score>" + str(round(score * 100, 2)) + "</score><level>NON-ABUSIVE</level><token><![CDATA[" + original + "]]></token></suspicion></result>"}

    print(result)
    return result, 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)