import pandas as pd
import requests
import cx_Oracle

SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

def get_nearest_station(tm_x, tm_y):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList"
    params = {
        "tmX": tm_x, "tmY": tm_y,
        "returnType": "json",
        "serviceKey": SERVICE_KEY,
        "ver": "1.1"
    }
    try:
        res = requests.get(url, params=params)
        items = res.json().get("response", {}).get("body", {}).get("items", [])
        if not items:
            return None
        return items[0]["stationName"]
    except Exception as e:
        print(f"[❌] API 오류: {e}")
        return None

def save_to_oracle(csv_path, oracle_info):
    df = pd.read_csv(csv_path)
    conn = cx_Oracle.connect(**oracle_info)
    cur = conn.cursor()
    for idx, row in df.iterrows():
        dong = row["동이름"]
        tm_x = row["TM_X"]
        tm_y = row["TM_Y"]
        station = get_nearest_station(tm_x, tm_y)
        print(f"{dong} → {station}")

        # 이미 row가 있으면 UPDATE, 없으면 INSERT (MERGE도 가능)
        cur.execute("""
            MERGE INTO DAEJEON_STATION_MAP t
            USING (SELECT :dong AS DONG_NAME FROM dual) s
            ON (t.DONG_NAME = s.DONG_NAME)
            WHEN MATCHED THEN
                UPDATE SET STATION_NAME=:station, TM_X=:tm_x, TM_Y=:tm_y
            WHEN NOT MATCHED THEN
                INSERT (DONG_NAME, STATION_NAME, TM_X, TM_Y)
                VALUES (:dong, :station, :tm_x, :tm_y)
        """, dong=dong, station=station, tm_x=tm_x, tm_y=tm_y)
        conn.commit()
    cur.close()
    conn.close()
    print("DB 저장 완료!")

if __name__ == "__main__":
    oracle_info = {
        "user": "ef",
        "password": "ef",
        "dsn": cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
    }
    save_to_oracle("대전_TM_좌표목록.csv", oracle_info)
