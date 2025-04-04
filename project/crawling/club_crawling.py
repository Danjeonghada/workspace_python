import requests
from bs4 import BeautifulSoup
import re
import cx_Oracle

url = 'https://fconline.nexon.com/datacenter'
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# club_id 추출용 정규식
pattern = re.compile(r"SetAbilitySearch\('(\d+)',\s*'n4TeamId'")

club_data = []

for a in soup.select('a[class^=club_item]'):
    league_id = a.get('data-no')
    onclick = a.get('onclick')
    name_tag = a.find('span')
    club_name = name_tag.text.strip() if name_tag else None

    if league_id and onclick and club_name:
        match = pattern.search(onclick)
        if match:
            club_id = int(match.group(1))
            league_id = int(league_id)
            club_data.append((club_id, club_name, league_id))

print(f"✔ 클럽 수집 완료: {len(club_data)}개")

# DB 연결
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

# INSERT
inserted = 0
for club_id, club_name, league_id in club_data:
    try:
        cursor.execute("""
            INSERT INTO clubs (club_id, club_name, league_id)
            VALUES (:1, :2, :3)
        """, [club_id, club_name, league_id])
        inserted += 1
    except cx_Oracle.IntegrityError:
        print(f"⚠ 중복 건너뜀: {club_name} (ID: {club_id})")

conn.commit()
cursor.close()
conn.close()

print(f"✅ 클럽 DB 삽입 완료: {inserted}건 저장됨")
