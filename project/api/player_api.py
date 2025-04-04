import requests
import cx_Oracle

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# API 호출
url = 'https://open.api.nexon.com/static/fconline/meta/spid.json'
response = requests.get(url)
spid_data = response.json()

# Oracle 연결
conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

for item in spid_data:
    spid = item["id"]
    season_id = spid // 1_000_000
    player_id = spid % 1_000_000
    name = item["name"]

    # player_cards 테이블에 INSERT
    try:
        cursor.execute("INSERT INTO player_cards (card_id, player_id, season_id) VALUES (:1, :2, :3)", [spid, player_id, season_id])
        print(f"[✔] 카드 저장: card_id = {spid}, player_id = {player_id}, season_id = {season_id}")
    except cx_Oracle.IntegrityError:
        print(f"[⚠️] 카드 중복: card_id = {spid}")

    # players 테이블에 INSERT
    try:
        cursor.execute("INSERT INTO players (player_id, player_name) VALUES (:1, :2)", [player_id, name])
        print(f"[✔] 선수 저장: player_id = {player_id}, name = {name}")
    except cx_Oracle.IntegrityError:
        print(f"[⚠️] 선수 중복: player_id = {player_id}")

# 커밋 및 정리
conn.commit()
cursor.close()
conn.close()
print("✅ 데이터 저장 완료")
