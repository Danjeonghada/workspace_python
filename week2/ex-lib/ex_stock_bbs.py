import pandas as pd
import requests
import json
from week2.ex_db.DBManager import DBManager
db = DBManager()
sql_merge = """
MERGE INTO stock_bbs a
USING DUAL
ON(   a.rsno = :rsno
  AND a.discussion_id = :discussion_id
  AND a.item_code = :item_code)
WHEN MATCHED THEN
    UPDATE SET a.read_count = :read_count
             , a.good_count = :good_count
             , a.bad_count = :bad_count
             , a.comment_count = : comment_count
             , a.update_date = SYSDATE
WHEN NOT MATCHED THEN
    INSERT (a.rsno, a.discussion_id, a.item_code, a.title, a.bbs_contents, a.writer_id
          , a.read_count, a.good_count, a.bad_count, a.comment_count, a.end_path, a.update_date)
    VALUES (:rsno, :discussion_id, :item_code, :title, :bbs_contents, :writer_id, :read_count
          , :good_count, :bad_count, :comment_count, :end_path, TO_DATE(:update_date, 'YYYY-MM-DD HH24:MI:SS'))
"""
# db에서 krx_yn이 Y인 종목만 요청
def get_bbs(code):
    url = f"https://m.stock.naver.com/front-api/discuss?discussionType=localStock&itemCode={code}&size=100"
    res = requests.get(url)
    json_data = json.loads(res.text)
    for v in json_data['result']:
        row= {
            "rsno": v.get("rsno", None),
            "discussion_id": v.get("discussionId", None),
            "item_code": v.get("itemCode", ""),  # itemCode → item_code 변경
            "title": v.get("title", ""),
            "bbs_contents": v.get("contents", "")[:1300],  # ✅ 수정됨
            "writer_id": v.get("writerId", ""),
            "read_count": v.get("readCount", 0),
            "good_count": v.get("goodCount", 0),
            "bad_count": v.get("badCount", 0),
            "comment_count": v.get("commentCount", 0),
            "end_path": v.get("endPath", ""),
            "update_date": v.get("date", "")[:19]
        }
        try:
            print(row)
            db.insert(sql_merge, row)
        except Exception as e:
            print(str(e))
if __name__ == '__main__':
    db = DBManager()
    conn = db.get_connection()
    selec_sql = """ SELECT krx_code
                         , krx_name
                         , krx_market
                    FROM tb_krx
                    WHERE krx_yn = 'Y'
    
    """
    df = pd.read_sql(con=conn, sql=selec_sql)
    for i, v in df.iterrows():
        code = v["KRX_CODE"]
        get_bbs(code)
    print("완료")
