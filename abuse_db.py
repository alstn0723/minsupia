import flask_reqparse as reqparse
from flask import Flask
from tensorflow.keras.preprocessing.sequence import pad_sequences
import abuse_tester as at
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
    parser.add_argument('memberUid')
    parser.add_argument('userId')

    sentence = parser.parse_args()['content']
    member_Uid = parser.parse_args()['memberUid']
    user_Uid = parser.parse_args()['userId']

    org_idx = sentence.find(":")

    #Org Name : 스트링 제거
    if (org_idx == -1):
        sentence = sentence
    else:
        sentence = sentence[org_idx:]

    original = sentence


    print(sentence)
    MODEL, BOW = at.Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')
    tokens = at.Preprocess_Predict(sentence)

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

    #CONTENT TABLE
    sql = """INSERT INTO E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID, MEMBERUID, USERUID, CONTENT, SCORE) VALUES (CONTENT_SPAM_SCORE_SEQ.NEXTVAL, :1, :2, :3, :4)"""
    cur.execute(sql, (member_Uid, user_Uid, sentence, total_score))

    #TOKEN TABLE
    for j in range(len(tokens)):
        sql = """INSERT INTO E_TOKEN_SPAM_SCORE(TOKENSPAMSCOREUID, CONTENTSPAMSCOREUID, TOKEN, SCORE) VALUES (TOKEN_SPAM_SCORE_SEQ.NEXTVAL, CONTENT_SPAM_SCORE_SEQ.CURRVAL, :1, :2)"""
        cur.execute(sql, (tokens[j], token_score[j]))

    #CONTENT_SPAM_SCORE_SEQ.CURRVAL 꺼내서 json 리턴 해야됨

    #DB에 저장 후 종료
    oc.Close_Conn(conn)


    return 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
