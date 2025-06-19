import cx_Oracle
import pandas as pd

# DB 연결
conn = cx_Oracle.connect("kwj", "kwj", "192.168.0.44:1521/xe")
cursor = conn.cursor()

# 2020년 이후 제품
fan = pd.read_excel("./product_list/fan.xlsx")
fan =fan[fan['company_name'] != fan['model_name']]
fan = fan.drop_duplicates(subset=['company_name', 'model_name'])
fan['item_key'] = fan['item_key'].astype(int)

airconditioning = pd.read_excel("./product_list/에어컨.xlsx")
airconditioning =airconditioning[airconditioning['company_name'] != airconditioning['model_name']]
airconditioning = airconditioning.drop_duplicates(subset=['company_name', 'model_name'])

airconditioning['item_key'] = airconditioning['item_key'].fillna(2).astype(int)
airconditioning['monthly_electricity'] = airconditioning['monthly_electricity'].astype(float)
airconditioning['energy_efficiency'] = airconditioning['energy_efficiency'].astype(float)

microwave_oven = pd.read_excel("./product_list/전자레인지.xlsx")
microwave_oven =microwave_oven[microwave_oven['company_name'] != microwave_oven['model_name']]
microwave_oven = microwave_oven.drop_duplicates(subset=['company_name', 'model_name'])
microwave_oven['item_key'] = microwave_oven['item_key'].astype(int)
microwave_oven['standby_power_watt'] = microwave_oven['standby_power_watt'].astype(float)
microwave_oven['on_mode_power_watt'] = microwave_oven['on_mode_power_watt'].replace(' ', '', regex=True)
microwave_oven['on_mode_power_watt'] = microwave_oven['on_mode_power_watt'].astype(int)

router = pd.read_excel("./product_list/공유기.xlsx")
router =router[router['company_name'] != router['model_name']]
router = router.drop_duplicates(subset=['company_name', 'model_name'])
router['item_key'] = router['item_key'].astype(int)
router['rated_power_watt'] = router['rated_power_watt'].astype(float)
router['standby_power_watt'] = router['standby_power_watt'].astype(float)

bidet = pd.read_excel("./product_list/비데.xlsx")
bidet =bidet[bidet['company_name'] != bidet['model_name']]
bidet = bidet.drop_duplicates(subset=['company_name', 'model_name'])
bidet['item_key'] = bidet['item_key'].astype(int)
bidet['standby_power_watt'] = bidet['standby_power_watt'].astype(float)
bidet['off_mode_power_watt'] = bidet['off_mode_power_watt'].astype(float)


print(fan.columns)

fan_insert = """
    INSERT INTO fan (item_key, company_name, model_name, meps)
    VALUES (:1, :2, :3, :4)
"""
for _, row in fan.iterrows():
    cursor.execute(fan_insert, (row["item_key"], row["company_name"], row["model_name"], row["meps"]))

airconditioning_insert = """
    INSERT INTO airconditioning (item_key, company_name, model_name, monthly_electricity, energy_efficiency)
    VALUES (:1, :2, :3, :4, :5)
"""
for _, row in airconditioning.iterrows():
    cursor.execute(airconditioning_insert, (row["item_key"], row["company_name"], row["model_name"], row["monthly_electricity"], row["energy_efficiency"]))

router_insert = """
    INSERT INTO router (item_key, company_name, model_name, rated_power_watt, standby_power_watt)
    VALUES (:1, :2, :3, :4, :5)
"""
for _, row in router.iterrows():
    cursor.execute(router_insert, (row["item_key"], row["company_name"], row["model_name"], row["rated_power_watt"], row["standby_power_watt"]))

bidet_insert = """
    INSERT INTO bidet (item_key, company_name, model_name, standby_power_watt, off_mode_power_watt)
    VALUES (:1, :2, :3, :4, :5)
"""
for _, row in bidet.iterrows():
    cursor.execute(bidet_insert, (row["item_key"], row["company_name"], row["model_name"], row["standby_power_watt"], row["off_mode_power_watt"]))

microwave_oven_insert = """
    INSERT INTO microwave_oven (item_key, company_name, model_name, standby_power_watt, on_mode_power_watt)
    VALUES (:1, :2, :3, :4, :5)
"""
for _, row in microwave_oven.iterrows():
    cursor.execute(microwave_oven_insert, (row["item_key"], row["company_name"], row["model_name"], row["standby_power_watt"], row["on_mode_power_watt"]))


# 커밋하고 닫기
conn.commit()
cursor.close()
conn.close()

print("✅ 모든 데이터 삽입 완료!")