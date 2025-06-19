import pandas as pd
import cx_Oracle
import re

# 1. 엑셀 파일 경로
excel_path = r'/teamPro/1차 전기요금 모델링/data\단지_기본정보_대전.xlsx'

# 2. 엑셀 불러오기
df = pd.read_excel(excel_path, dtype=str)

# 3. 필요한 열 추출 및 컬럼명 매핑
df = df[['단지코드', '단지명', '시도', '시군구', '동리', '법정동주소']].copy()
df.rename(columns={
    '단지코드': 'kapt_code',
    '단지명': 'kapt_name',
    '시도': 'sido',
    '시군구': 'district',
    '동리': 'dong',
    '법정동주소': 'address_raw'
}, inplace=True)


# 번지수만 추출
def extract_address_num(full_addr):
    match = re.search(r'\b(\d{1,4}-?\d*)\b', full_addr)
    return match.group(1) if match else None


df['address_num'] = df['address_raw'].apply(extract_address_num)

# 4. Oracle DB 연결
dsn = cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
conn = cx_Oracle.connect(user="kwj", password="kwj", dsn=dsn)
cursor = conn.cursor()

# 5. INSERT SQL (address_num 기준)
insert_sql = """
    INSERT INTO apartments (
        kapt_code, kapt_name, sido, district, dong, address_num
    ) VALUES (
        :1, :2, :3, :4, :5, :6
    )
"""

# 6. 행별 삽입 처리
for idx, row in df.iterrows():
    try:
        cursor.execute(insert_sql, (
            row['kapt_code'], row['kapt_name'], row['sido'], row['district'], row['dong'], row['address_num']
        ))
    except cx_Oracle.IntegrityError:
        print(f"[중복 건너뜀] {row['kapt_code']} - {row['kapt_name']}")
    except Exception as e:
        print(f"[에러 발생] {row['kapt_code']} - {e}")

conn.commit()
cursor.close()
conn.close()
print("✅ 아파트 데이터 삽입 완료")
