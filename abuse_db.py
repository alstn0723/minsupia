import flask_reqparse as reqparse
from flask import Flask
from tensorflow.keras.preprocessing.sequence import pad_sequences
import abuse_base as ab
import oracle_conn as oc



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

    oc.Oracle_Init()
    #Connection, Cursor 받아오기
    conn, cur = oc.Oracle_Conn("d_alstn0723", "steam9588!", "192.168.2.101:1521/DCDB")

    sql = """INSERT INTO E_CONTENT_SPAM_SCORE (CONTENT, SCORE) VALUES (%s, %s)"""
    cur.execute(sql, (original, total_score))

    for i in range(len(tokens)):
        sql = """INSERT INTO E_TOKEN_SPAM_SCORE (TOKEN, SCORE) VALUES (%s, %s)"""
        cur.execute(sql, ((tokens[i]), token_score[i]))

    oc.Close_Conn(conn)


    return 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
