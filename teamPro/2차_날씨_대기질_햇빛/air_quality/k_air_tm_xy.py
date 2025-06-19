import pandas as pd
import requests
import time
from pyproj import Transformer

# 서비스키
SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

# pyproj 변환기: WGS84 → TM
transformer = Transformer.from_crs("epsg:4326", "epsg:2097", always_xy=True)

# TM 좌표 API 요청 함수
def get_tm_by_dong_api(dong_name):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt"
    params = {
        "serviceKey": SERVICE_KEY,
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "umdName": dong_name
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        filtered = [item for item in items if item.get("sidoName") == "대전광역시"]
        if not filtered:
            return None, None
        return float(filtered[0]["tmX"]), float(filtered[0]["tmY"])
    except Exception as e:
        print(f"[❌] '{dong_name}' API 오류: {e}")
        return None, None

# 위경도 기반 TM 좌표 계산 함수
def get_tm_from_latlon(lat, lon):
    return transformer.transform(lon, lat)

# TM 좌표 저장 함수
def save_tm_coords_from_excel(input_path="xy_code_daejeon.xlsx", output_path="tm_coords_from_api.csv"):
    df = pd.read_excel(input_path)
    df['TM_X'] = None
    df['TM_Y'] = None

    for i, row in df.iterrows():
        dong = row['3단계']
        print(f"\n📍 요청 동: {dong}")
        tm_x, tm_y = get_tm_by_dong_api(dong)

        # 실패 시 엑셀 위경도 데이터를 변환
        if tm_x is None or tm_y is None:
            try:
                lat = float(row['위도(초/100)'])
                lon = float(row['경도(초/100)'])
                tm_x, tm_y = get_tm_from_latlon(lat, lon)
                print(f"🔁 TM 좌표 변환 (위경도 기준): X={tm_x}, Y={tm_y}")
            except Exception as e:
                print(f"[⚠️] '{dong}' 변환 실패: {e}")
                continue

        # TM 좌표 저장
        df.at[i, 'TM_X'] = tm_x
        df.at[i, 'TM_Y'] = tm_y

        time.sleep(0.3)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n📁 TM 좌표 저장 완료 → {output_path}")

# 실행
if __name__ == "__main__":
    save_tm_coords_from_excel()

