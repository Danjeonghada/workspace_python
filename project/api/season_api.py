import requests
import cx_Oracle

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# API 호출
url = 'https://open.api.nexon.com/static/fconline/meta/seasonid.json'
response = requests.get(url)
spid_data = response.json()

# Oracle 연결
conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

for item in spid_data:
    sid = item["seasonId"]
    name = item["className"]
    img = item["seasonImg"]

    # player_cards 테이블에 INSERT
    try:
        cursor.execute("INSERT INTO seasons (season_id, class_name, season_img) VALUES (:1, :2, :3)", [sid, name, img])
        print(f"[✔] 카드 저장: card_id = {sid}, class_name = {name}, season_img = {img}")
    except cx_Oracle.IntegrityError as e:
        print(f"[⚠️] 카드 중복 or 오류: season_id = {sid}, 이유: {e}")

# 커밋 및 정리
conn.commit()
cursor.close()
conn.close()
print("✅ 데이터 저장 완료")
