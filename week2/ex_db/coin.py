import sqlite3
import requests
import json
import datetime

def get_coin():
    conn = sqlite3.connect('mydb.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM tb_coin")
    sql = """ INSERT INTO tb_coin_detail
             VALUES(:1, :2, :3)"""
    now = datetime.datetime.now()
    format_now = now.strftime("%Y-%m-%d %H:%M:%S")
    rows = cur.fetchall()
    for row in rows:
        market = row[0]
        kr_nm = row[1]
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        res = requests.get(url)
        if res.status_code == 200:
            json_data = json.loads(res.text)[0]
            price = "{:.15f}".format(json_data['trade_price'])
            cur.execute(sql, [market, price, format_now])
            conn.commit()
    conn.close()