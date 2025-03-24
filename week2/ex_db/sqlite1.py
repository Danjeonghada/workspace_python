import sqlite3
# 경량 db, 파일 형태
# 없으면 만들고, 있으면 접속함
conn = sqlite3.connect("mydb.db")
# conn = sqlite3.connect(":memory:") # 일회성 사용
sql ="""
    CREATE TABLE tb_coin(
        market VARCHAR2(20)
       ,kr_nm  VARCHAR2(100)
       ,en_nm  VARCHAR2(100)
    )
"""
cur = conn.cursor()
cur.execute(sql) # 쿼리 실행
conn.close()