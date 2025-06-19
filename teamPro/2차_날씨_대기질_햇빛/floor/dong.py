import pandas as pd

# ✅ 파일 경로 지정
file_complex = "한국부동산원_공동주택 단지 식별정보_기본정보_20240809_대전추출.xlsx"
file_building = "한국부동산원_공동주택 단지 식별정보_동정보_20240809.xlsx"

# ✅ 사용할 컬럼 목록 정의
columns_complex = ['단지고유번호', '읍면동', '지번', '단지명_공시가격', '단지종류', '동수', '세대수']
columns_building = ['단지고유번호', '동명_공시가격', '동명_건축물대장', '동명_도로명주소', '지상층수']

# ✅ 엑셀 파일 불러오기 (단지고유번호는 문자열로 읽기) + 필요한 컬럼만 선택
df_complex = pd.read_excel(file_complex, dtype={'단지고유번호': str})[columns_complex]
df_building = pd.read_excel(file_building, dtype={'단지고유번호': str})[columns_building]

# ✅ 병합 (1:N)
df_merged = pd.merge(df_complex, df_building, on="단지고유번호", how="left")

# ✅ 병합 결과 저장
output_file = "병합_단지동_필요컬럼.xlsx"
df_merged.to_excel(output_file, index=False)

print(f"[완료] 병합된 파일이 저장되었습니다: {output_file}")

