import tensorflow as tf
import cx_Oracle
import os
import pandas as pd
import abuse_tester as at
import time
from tensorflow.keras.preprocessing.sequence import pad_sequences

MODEL, BOW = at.Load_Model("Abuse_Detect.h5", "Abuse_Tokenizer.pickle")


def ACC_Check(sentence):

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

    total_score = round(total_score * 100, 4)
    return sentence, total_score, tokens, token_score


def Oracle_Init():
    #환경변수 설정
    LOCATION = r"C:\instantclient_21_3"
    os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]

    #Initialize
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_3")


def Oracle_Conn(ID, PASSWORD, HOSTPORTSERVICE):
    #접속
    conn = cx_Oracle.connect(ID, PASSWORD, HOSTPORTSERVICE)
    cursorname = conn.cursor()#커서 가져오기

    return conn, cursorname

def Close_Conn(conn):
    conn.commit()
    conn.close()

start = time.time()

Oracle_Init()

# 연결 됐는지 버전 체크
#print(cx_Oracle.clientversion())

conn, cur = Oracle_Conn("d_alstn0723", "steam9588!", "192.168.2.101:1521/DCDB")


data = pd.read_csv("inbound.csv")
data = data['CONTENT']
'''
sql = "DELETE FROM E_CONTENT_SPAM_SCORE"
cur.execute(sql)
sql = "DELETE FROM E_TOKEN_SPAM_SCORE"
cur.execute(sql)
'''
for i in range(len(data)):
    print(i)
    sentence, total_score, tokens, token_score = ACC_Check(data[i])

    sql = """INSERT INTO E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID, MEMBERUID, USERUID, CONTENT, SCORE) VALUES (CONTENT_SPAM_SCORE_SEQ.NEXTVAL, :1, :2, :3, :4)"""
    cur.execute(sql, (17115, 17115, sentence, total_score))

    for j in range(len(tokens)):
        sql = """INSERT INTO E_TOKEN_SPAM_SCORE(TOKENSPAMSCOREUID, CONTENTSPAMSCOREUID, TOKEN, SCORE) VALUES (TOKEN_SPAM_SCORE_SEQ.NEXTVAL, CONTENT_SPAM_SCORE_SEQ.CURRVAL, :1, :2)"""
        cur.execute(sql, (tokens[j], token_score[j]))

Close_Conn(conn)

end = time.time()

print(end-start)
#sql developer 쿼리랑 다르게 세미콜론 있으면 오류남


#sql = "INSERT INTO sentences (content, score) VALUES (%s ,%s)"
#sql = "DELETE FROM sentences WHERE content LIKE 'sentence'"
#sql = "DELETE FROM inbound_score"
#sql = "DROP TABLE inbound_score"


#cur.execute(CSSSQL)






'''
CSSSQL =     """CREATE TABLE IF NOT EXISTS E_CONTENT_SPAM_SCORE(
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                MEMBERUID NUMBER DEFAULT 0 NOT NULL,
                USERUID NUMBER DEFAULT 0 NOT NULL,
                CONTENT VARCHAR(2000),
                SCORE NUMBER DEFAULT 0 NOT NULL,
                CREATEDATE DATE DEFAULT 0 NOT NULL,
                CONSTRAINT E_CONTENT_SPAM_SOCRE PRIMARY KEY (CONTENTSPAMSCOREUID) USING INDEX  TABLESPACE ${TABLESPACE},
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

TSSSQL =     """CREATE TABLE IF NOT EXISTS E_TOKEN_SPAM_SCORE(
                TOKENSPAMSCOREUID NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                TOKEN VARCHAR(2000),
                SCORE NUMBER DEFAULT 0 NOT NULL,
                CONSTRAINT E_TOKEN_SPAM_SCORE PRIMARY KEY (TOKENSPAMSCOREUID) USING INDEX TABLESPACE ${TABLESPACE},
                FOREIGN KEY CONTENTSPAMSCOREUID REFERENCES E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID),
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

OSCSQL =     """CREATE TABLE E_OUTBOUND_SPAM_CHECK(
                OUTBOUNDSPAMCHECK NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                USETYPE NUMVER DEFAULT 0 NOT NULL,
                USEUID NUMBER NOT NULL,
                CONSTRAINT E_OUTBOUND_SPAM_CHECK PRIMARY KEY (OUTBOUNDSPAMCHECK) USING INDEX TABLESPACE ${TABLESPACE},
                FOREIGN KEY CONTENTSPAMSCOREUID REFERENCES E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID),
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

ISCSQL =     """CREATE TABLE E_INBOUND_SPAM_CHECK(
                INBOUNDSPAMCHECKUID NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                INBOUNDCHECKUID NUMBER NOT NULL,
                CONSTRAINT E_INBOUND_SPAM_CHECK PRIMARY KEY (INBOUNDSPAMCHECKUID) USING INDEX TABLESPACE ${TABLESPACE},
                FOREIGN KEY CONTENTSPAMSCOREUID REFERENCES E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID),
                CHARACTER SET utf8 COLLATE utf8_general_ci"""
'''