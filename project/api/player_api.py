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

# 커밋할 데이터를 저장할 리스트
player_cards_data = []
players_data = []

for item in spid_data:
    spid = item["id"]
    season_id = spid // 1_000_000
    player_id = spid % 1_000_000
    name = item["name"]

    # player_cards 테이블에 중복 체크 후 추가
    cursor.execute("SELECT 1 FROM player_cards WHERE card_id = :1", [spid])
    if cursor.fetchone() is None:  # card_id가 없으면
        player_cards_data.append((spid, player_id, season_id))
        print(f"✔ player_cards 데이터 추가: {spid}")
    else:
        print(f"⚠️ player_cards 데이터 중복: {spid}")

    # players 테이블에 중복 체크 후 추가
    cursor.execute("SELECT 1 FROM players WHERE player_id = :1", [player_id])
    if cursor.fetchone() is None:  # player_id가 없으면
        players_data.append((player_id, name))
        print(f"✔ players 데이터 추가: {player_id}")
    else:
        print(f"⚠️ players 데이터 중복: {player_id}")

# 100개씩 커밋
def commit_data(data, table):
    if table == "player_cards":
        cursor.executemany("INSERT INTO player_cards (card_id, player_id, season_id) VALUES (:1, :2, :3)", data)
    elif table == "players":
        cursor.executemany("INSERT INTO players (player_id, player_name) VALUES (:1, :2)", data)
    conn.commit()
    print(f"✔ {table} 데이터 커밋됨.")

# 100개씩 커밋하기
commit_data(player_cards_data[:100], "player_cards")
commit_data(players_data[:100], "players")

# 남은 데이터 커밋하기
commit_data(player_cards_data[100:], "player_cards")
commit_data(players_data[100:], "players")

# 정리
cursor.close()
conn.close()
print("✅ 데이터 저장 완료")
