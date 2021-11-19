from flask import Flask, request
import abuse_tester as at
import oracle_conn as oc
import logging.handlers


#일 단위 로그파일 생성

mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)
rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename='log/'+'monitoring.log', when='midnight', interval=1, encoding='utf-8')
fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
rotatingHandler.setFormatter(fomatter)
mylogger.addHandler(rotatingHandler)


#DB구동
oc.Oracle_Init()

#MODEL 불러오기
MODEL, BOW = at.Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')

app = Flask(__name__)


@app.route('/spam/nlp', methods=['POST'])
def abuse_predict():

    logging.info('prediction api called.')

    sentence = request.json.get('content')
    member_Uid = int(request.json.get('memberUid'))
    user_Uid = int(request.json.get('userId'))

    if type(sentence) != str:
        raise ValueError("Content does not exist")

    elif type(member_Uid) != int:
        raise ValueError("member_Uid Error occured.")

    elif type(user_Uid) != int:
        raise ValueError("user_Uid Error occured.")

    org_idx = sentence.find(":")

    #Org Name : 스트링 제거
    if (org_idx == -1):
        sentence = sentence
    else:
        sentence = sentence[org_idx:]

    original = sentence

    #예측 진행
    sentence, total_score, tokens, token_score = at.ACC_Check(sentence, MODEL, BOW)

    logging.info("Sentence ==> {0}".format(sentence))
    logging.info("Sentence Score : {0}".format(total_score))
    logging.info("Tokens : {0}".format(tokens))
    logging.info("Token_scores : {0}".format(token_score))


    # Connection, Cursor 받아오기
    conn, cur = oc.Oracle_Conn("d_alstn0723", "steam9588!", "192.168.2.101:1521/DCDB")

    logging.info("DB connected")

    #CONTENT TABLE
    sql = """INSERT INTO E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID, MEMBERUID, USERUID, CONTENT, SCORE) VALUES (CONTENT_SPAM_SCORE_SEQ.NEXTVAL, :1, :2, :3, :4)"""
    cur.execute(sql, (member_Uid, user_Uid, sentence, total_score))

    logging.info("E_CONTENT_SPAM_SCORE")

    #TOKEN TABLE
    for j in range(len(tokens)):
        sql = """INSERT INTO E_TOKEN_SPAM_SCORE(TOKENSPAMSCOREUID, CONTENTSPAMSCOREUID, TOKEN, SCORE) VALUES (TOKEN_SPAM_SCORE_SEQ.NEXTVAL, CONTENT_SPAM_SCORE_SEQ.CURRVAL, :1, :2)"""
        cur.execute(sql, (tokens[j], token_score[j]))

    logging.info("E_TOKEN_SPAM_SCORE")

    sql = """SELECT CONTENT_SPAM_SCORE_SEQ.CURRVAL FROM E_CONTENT_SPAM_SCORE"""
    cur.execute(sql)

    #CONTENTSPAMSCOREUID => PRIMARY KEY
    CSSU = cur.fetchall()[0][0]
    CSSU = {"contentSpamScoreUid":CSSU}

    #DB에 저장 후 커서 연결 종료
    oc.Close_Conn(conn)

    logging.info("DB closed")

    return CSSU

if __name__ == '__main__':
    app.run(host='192.168.3.184', port=5000)