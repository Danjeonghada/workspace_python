import pandas as pd
from week2.ex_db.DBManager import DBManager
from week2.ex_db.mylogger import make_logger
db = DBManager()
# 엑셀 읽어 오기
# query
sql ={"info_insert": """
    INSERT INTO tb_krx(krx_code, krx_name, krx_market, krx_volume)
    VALUES (:1, :2, :3, :4)
    
"""}
krx_df = pd.read_excel("krx.xlsx", engine="openpyxl")
print(krx_df.head())
for i, row in krx_df.iterrows():
    code = row["Code"]
    nm = row["Name"]
    market = row["Market"]
    vol = row["Volume"]
    print(f"{i}:{row['Name']}-{row['Code']}-{row['Market']}-{row['Volume']}")
    db.insert(sql['info_insert'], [code, nm, market, vol])
    # DB에 저장 ! tb_krx
