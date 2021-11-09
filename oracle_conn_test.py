import mariadb
import cx_Oracle
import os

LOCATION = r"C:\instantclient_21_3"
os.environ["PATH"] = LOCATION + ";" + os.environ["PATH"]
cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_3")

import abuse_build as ab


# Test to see if the cx_Oracle is recognized
print(cx_Oracle.clientversion())


conn = cx_Oracle.connect('d_alstn0723','steam9588!', "192.168.2.101:1521/DCDB")
# Get Cursor
cur = conn.cursor()

sql = "SELECT * FROM V_INTL_COST"
#sql = "CREATE TABLE IF NOT EXISTS inbound_score (id int(5) NOT NULL AUTO_INCREMENT PRIMARY KEY, content char(255), score float(8)) DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
#sql = "INSERT INTO sentences (content, score) VALUES (%s ,%s)"
#sql = "DELETE FROM sentences WHERE content LIKE 'sentence'"
#sql = "DELETE FROM inbound_score"
#sql = "DROP TABLE inbound_score"
cur.execute(sql)
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