import requests
from bs4 import BeautifulSoup
import re
import cx_Oracle

# 리그 리스트가 포함된 페이지
url = 'https://fconline.nexon.com/datacenter'
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# 리그 ID 추출용 정규식
pattern = re.compile(r"SetTeamOption\((\d+)\)")

league_data = []

for a in soup.select('a[class^=league_item]'):
    onclick = a.get('onclick')
    name_tag = a.find('span')
    league_name = name_tag.text.strip() if name_tag else None

    if onclick and league_name:
        match = pattern.search(onclick)
        if match:
            league_id = int(match.group(1))
            league_data.append((league_id, league_name))

print(f"✔ 리그 수집 완료: {len(league_data)}개")

# DB 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

# INSERT 실행
inserted = 0
for league_id, league_name in league_data:
    try:
        cursor.execute("""
            INSERT INTO leagues (league_id, league_name)
            VALUES (:1, :2)
        """, [league_id, league_name])
        inserted += 1
    except cx_Oracle.IntegrityError:
        print(f"⚠ 중복 건너뜀: {league_name} (ID: {league_id})")

conn.commit()
cursor.close()
conn.close()

print(f"✅ 리그 DB 삽입 완료: {inserted}건 저장됨")
