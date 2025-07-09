import pandas as pd
import cx_Oracle

# 1. 오라클 DB 연결
# 예시: 아이디: hr / 비번: 1234 / 호스트: localhost / 포트: 1521 / 서비스명: orcl
conn = cx_Oracle.connect('ef/ef@192.168.0.44:1521/xe')
# 예: conn = cx_Oracle.connect('hr/1234@localhost:1521/orcl')

# 2. DB에서 DONG 목록 가져오기
sql = "SELECT DISTINCT DONG FROM APARTMENTS_ADDRESS"
df_db = pd.read_sql(sql, conn)
db_dongs = set(df_db['DONG'].astype(str).str.strip())

# 3. 좌표목록 불러오기
df_coords = pd.read_csv('좌표목록.csv', encoding='utf-8')
coord_dongs = set(df_coords['3단계'].astype(str).str.strip())

# 4. 좌표목록에 없는 동 찾기
missing_dongs = db_dongs - coord_dongs

print("좌표목록.csv에 없는 동:")
for dong in missing_dongs:
    print(dong)

# 필요하다면 파일로 저장
pd.DataFrame({'미존재_동목록': list(missing_dongs)}).to_csv('미존재_동목록.csv', index=False, encoding='utf-8-sig')

# 5. DB 연결 종료
conn.close()
