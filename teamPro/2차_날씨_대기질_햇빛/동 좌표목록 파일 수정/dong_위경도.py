import pandas as pd

# 1. 엑셀에서 '3단계', '경도(초/100)', '위도(초/100)'만 추출 (컬럼명 확인!)
df_excel = pd.read_excel('xy_code_daejeon.xlsx', usecols=['3단계', '경도(초/100)', '위도(초/100)'])

# 2. 컬럼명 통일
df_excel = df_excel.rename(columns={'3단계': '동이름', '경도(초/100)': '경도', '위도(초/100)': '위도'})

# 3. 미존재_동목록_좌표.csv에서 '동이름', '위도', '경도'만 추출 (혹시 다른 이름이면 맞춰줘야 함)
df_missing = pd.read_csv('미존재_동목록_좌표.csv', usecols=['동이름', '위도', '경도'])

# 4. 합치기
df_all = pd.concat([df_excel, df_missing], ignore_index=True)

# 5. 중복 동이름 제거 (엑셀 값 우선)
df_all = df_all.drop_duplicates(subset=['동이름'], keep='first')

# 6. 최종 저장
df_all.to_csv('좌표목록_통합.csv', index=False, encoding='utf-8-sig')

print("완성된 파일: 좌표목록_통합.csv")
