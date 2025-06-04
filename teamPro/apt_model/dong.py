import pandas as pd
import cx_Oracle
import openpyxl

# 1. Oracle 연결
conn = cx_Oracle.connect("kwj", "kwj", "192.168.0.44:1521/xe")

# 2. 데이터 조회: apartments + electricity_fee JOIN
query = """
SELECT 
    a.dong,
    e.year,
    e.month,
    e.public_fee,
    e.private_fee,
    a.household
FROM apartments a
JOIN electricity_fee e ON a.kapt_code = e.kapt_code
"""
df = pd.read_sql(query, conn)
conn.close()

# 컬럼명 소문자로 변환
df.columns = df.columns.str.lower()

# 3. total_fee 계산
df["total_fee"] = df["public_fee"] + df["private_fee"]

# 4. groupby 후 집계
monthly_sum = df.groupby(["dong", "year", "month"], as_index=False).agg({
    "total_fee": "sum",
    "household": "sum"
})

# 5. 세대당 전기요금 계산
monthly_sum["final_monthly_fee"] = (monthly_sum["total_fee"] / monthly_sum["household"]).round()

# 6. 출력
result_df = monthly_sum[["dong", "year", "month", "final_monthly_fee"]]
result_df = result_df.sort_values(by=["year", "month", "dong"])
result_df["final_monthly_fee"] = result_df["final_monthly_fee"].astype(int)
result_df = result_df.reset_index(drop=True)
result_df.to_excel("동별세대당전기요금.xlsx", index=False)