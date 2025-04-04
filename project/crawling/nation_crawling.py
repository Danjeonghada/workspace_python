import requests
from bs4 import BeautifulSoup
import re
import cx_Oracle

# 1. 크롤링 대상 페이지
url = 'https://fconline.nexon.com/datacenter'  # 실제 URL 확인 필요
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# 2. nation_id 추출용 정규식
pattern = re.compile(r"SetAbilitySearch\('(\d+)',\s*'n4NationId'")

nation_data = []

for a in soup.select('a[class^=nationality_item]'):
    continent_id = a.get('data-no')
    onclick = a.get('onclick')
    name_tag = a.find('span')
    nation_name = name_tag.text.strip() if name_tag else None

    if continent_id and onclick and nation_name:
        match = pattern.search(onclick)
        if match:
            nation_id = int(match.group(1))
            continent_id = int(continent_id)
            nation_data.append((nation_id, nation_name, continent_id))

print(f"✔ 국가 수집 완료: {len(nation_data)}개")

# 3. Oracle DB 연결
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

# 4. INSERT 실행
inserted = 0
for nation_id, name, continent_id in nation_data:
    try:
        cursor.execute("""
            INSERT INTO nations (nation_id, nation_name, continent_id)
            VALUES (:1, :2, :3)
        """, [nation_id, name, continent_id])
        inserted += 1
    except cx_Oracle.IntegrityError:
        print(f"⚠ 중복 건너뜀: {name} (ID: {nation_id})")

conn.commit()
cursor.close()
conn.close()

print(f"✅ DB 삽입 완료: {inserted}건 저장됨")
