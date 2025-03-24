import pandas as pd
from reportlab.lib.pdfencrypt import reserved1

df = pd.DataFrame({"name": ["nick", "judy", "jack"]
                   ,"age": [10, 20, 22]})
print(df.head()) # head 내용 출력(기본 5행)
# 기존 열을 활용하여 새로운 열을 쉽게 만들 수 있음.
df['age_plus'] = df['age'] + 1
df['age_squared'] = df['age'] * df['age']
print(df.head())
# 다양한 내장 함수
total = df['age'].sum()
median = df['age'].quantile(0.5)
print(total, median)
# 병합 가능
df2 = pd.DataFrame({"name": ["nick", "judy", "jack"], "height": [182, 178, 175], "gender": ["M", "F", "M"]})
joined = df.set_index("name").join(df2.set_index('name'))
print(joined.head())
reset_joined = joined.reset_index()
print(reset_joined.head())
df_group = joined.groupby('gender').mean()
print(df_group)

# 엑셀 읽어 오기
krx_df = pd.read_excel("krx.xlsx", engine="openpyxl")
print(krx_df.head())
for i, row in krx_df.iterrows():
    print(f"{i}:{row['Name']}-{row['Code']}")