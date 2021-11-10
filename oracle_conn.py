import cx_Oracle
import os


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
