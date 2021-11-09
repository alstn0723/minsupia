import cx_Oracle
import os

def Oracle_Init():
    #환경변수 설정
    LOCATION = r"C:\instantclient_21_3"
    os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]

    #Initialize
    cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_3")

Oracle_Init()
# 연결 됐는지 버전 체크
print(cx_Oracle.clientversion())

def Oracle_Conn(cursorname):
    #접속
    conn = cx_Oracle.connect('d_alstn0723','steam9588!', "192.168.2.101:1521/DCDB")
    cursorname = conn.cursor()#커서 가져오기

    return cursorname

#sql developer 쿼리랑 다르게 세미콜론 있으면 오류남

CSSSQL =     """CREATE TABLE IF NOT EXISTS E_CONTENT_SPAM_SCORE(
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                MEMBERUID NUMBER DEFAULT 0 NOT NULL,
                USERUID NUMBER DEFAULT 0 NOT NULL,
                CONTENT VARCHAR(2000),
                SCORE NUMBER DEFAULT 0 NOT NULL,
                CREATEDATE DATE DEFAULT 0 NOT NULL,
                CONSTRAINT E_CONTENT_SPAM_SOCRE PRIMARY KEY (CONTENTSPAMSCOREUID) USING INDEX  TABLESPACE ${TABLESPACE}
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

TSSSQL =     """CREATE TABLE IF NOT EXISTS E_TOKEN_SPAM_SCORE(
                TOKENSPAMSCOREUID NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                TOKEN VARCHAR(2000),
                SCORE NUMBER DEFAULT 0 NOT NULL,
                CONSTRAINT E_TOKEN_SPAM_SCORE PRIMARY KEY (TOKENSPAMSCOREUID) USING INDEX TABLESPACE ${TABLESPACE}
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

OSCSQL =     """CREATE TABLE E_OUTBOUND_SPAM_CHECK(
                OUTBOUNDSPAMCHECK NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                USETYPE NUMVER DEFAULT 0 NOT NULL,
                USEUID NUMBER NOT NULL,
                CONSTRAINT E_OUTBOUND_SPAM_CHECK PRIMARY KEY (OUTBOUNDSPAMCHECK) USING INDEX TABLESPACE ${TABLESPACE}
                CHARACTER SET utf8 COLLATE utf8_general_ci"""

ISCSQL =     """CREATE TABLE E_INBOUND_SPAM_CHECK(
                INBOUNDSPAMCHECKUID NUMBER NOT NULL,
                CONTENTSPAMSCOREUID NUMBER NOT NULL,
                INBOUNDCHECKUID NUMBER NOT NULL,
                CONSTRAINT E_INBOUND_SPAM_CHECK PRIMARY KEY (INBOUNDSPAMCHECKUID) USING INDEX TABLESPACE ${TABLESPACE}
                CHARACTER SET utf8 COLLATE utf8_general_ci"""


#sql = "INSERT INTO sentences (content, score) VALUES (%s ,%s)"
#sql = "DELETE FROM sentences WHERE content LIKE 'sentence'"
#sql = "DELETE FROM inbound_score"
#sql = "DROP TABLE inbound_score"


#cur.execute(CSSSQL)

for i in cur:
    print(i)

conn.close()

'''

for i in range(len(data)):
    result = at.ACC_Check(data[i])
    sql = "INSERT INTO inbound_score (content, score) VALUES (%s ,%s)"
    cur.execute(sql, (data[i], result))
    conn.commit()

conn.close()
'''