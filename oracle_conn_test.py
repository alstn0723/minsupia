import oracle_conn as oc
import time
import pandas as pd
import abuse_tester as at

start = time.time()
MODEL, BOW = at.Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')

oc.Oracle_Init()

conn, cur = oc.Oracle_Conn("d_alstn0723", "steam9588!", "192.168.2.101:1521/DCDB")


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
    sentence, total_score, tokens, token_score = at.ACC_Check(data[i], MODEL, BOW)

    sql = """INSERT INTO E_CONTENT_SPAM_SCORE(CONTENTSPAMSCOREUID, MEMBERUID, USERUID, CONTENT, SCORE) VALUES (CONTENT_SPAM_SCORE_SEQ.NEXTVAL, :1, :2, :3, :4)"""
    cur.execute(sql, (17115, 17115, sentence, total_score))

    for j in range(len(tokens)):
        sql = """INSERT INTO E_TOKEN_SPAM_SCORE(TOKENSPAMSCOREUID, CONTENTSPAMSCOREUID, TOKEN, SCORE) VALUES (TOKEN_SPAM_SCORE_SEQ.NEXTVAL, CONTENT_SPAM_SCORE_SEQ.CURRVAL, :1, :2)"""
        cur.execute(sql, (tokens[j], token_score[j]))

oc.Close_Conn(conn)

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
