import sqlite3
import requests
import json
url = "https://api.upbit.com/v1/market/all"
sql = """
    INSERT INTO tb_coin
    VALUES(:1, :2, :3)
"""
res = requests.get(url)
json_data = json.loads(res.text)
conn = sqlite3.connect("mydb.db")
cur = conn.cursor()
for row in json_data:
    cur.execute(sql,  [ row['market'], row['korean_name']
                      , row['english_name'] ])
conn.commit()
conn.close()
print("종료!")