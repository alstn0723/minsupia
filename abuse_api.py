import flask_reqparse as reqparse
from flask import Flask
from tensorflow.keras.models import load_model
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re, pickle
import spacy
import abuse_base as ab



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
    MODEL, BOW = ab.Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')
    tokens = ab.Preprocess_Predict(sentence)

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


    if(total_score > 0.5):
        result = {"spamResult": "<result><totalscore>" + str(round(total_score * 100, 2)) + "</totalscore><totallevel>ABUSIVE</totallevel><suspicion><type>nlp</type><score>" + str(token_score) + "</score><level>ABUSIVE</level><token>" + str(tokens) + "></token></suspicion></result>"}

    else:
        result = {"spamResult": "<result><totalscore>" + str(round(total_score * 100, 2)) + "</totalscore><totallevel>NON-ABUSIVE</totallevel><suspicion><type>nlp</type><score>" + str(token_score) + "</score><level>NON-ABUSIVE</level><token>" + str(tokens) + "</token></suspicion></result>"}

    print(result)
    return result, 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
