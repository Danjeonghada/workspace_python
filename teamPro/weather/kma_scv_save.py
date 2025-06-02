import pandas as pd
import os

# 1. 파일 경로
BASE_DIR = "../weather_model"
excel_file = os.path.join(BASE_DIR, "xy_code_daejeon.xlsx")
csv_file = os.path.join(BASE_DIR, "좌표목록.csv")

# 2. 엑셀 읽기
df = pd.read_excel(excel_file)

# 3. NaN 제거 및 필요한 열 추출
df = df[df['3단계'].notna()]
columns_to_save = ['3단계', '격자 X', '격자 Y']
df_filtered = df[columns_to_save].drop_duplicates()

# 4. CSV 저장
df_filtered.to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"[완료] 정리된 동 좌표 CSV 저장됨: {csv_file}")
