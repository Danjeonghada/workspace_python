import pandas as pd
import requests

# 서비스 키
SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

def grade_to_text(code):
    return {
        "1": "좋음",
        "2": "보통",
        "3": "나쁨",
        "4": "매우나쁨"
    }.get(str(code), "-")


def get_nearest_station(tm_x, tm_y):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList"
    params = {
        "tmX": tm_x,
        "tmY": tm_y,
        "returnType": "json",
        "serviceKey": SERVICE_KEY,
        "ver": "1.1"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        if not items:
            return None
        return items[0]["stationName"]
    except Exception as e:
        print(f"[❌] 측정소 API 오류: {e}")
        return None

def get_air_quality(station_name):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {
        "stationName": station_name,
        "returnType": "json",
        "serviceKey": SERVICE_KEY,
        "dataTerm": "DAILY",
        "ver": "1.3"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        if not items:
            return None
        return items[0]
    except Exception as e:
        print(f"[❌] 대기질 API 오류: {e}")
        return None

def run_air_quality_flow(dong_name, coord_file="tm_coords_from_api.csv"):
    df = pd.read_csv(coord_file)
    row = df[df["3단계"] == dong_name]
    if row.empty:
        print(f"[❌] 엑셀 파일에서 '{dong_name}' 동을 찾을 수 없습니다.")
        return

    tm_x, tm_y = row.iloc[0]["TM_X"], row.iloc[0]["TM_Y"]
    print(f"\n📍 '{dong_name}' 동의 TM 좌표 → X={tm_x}, Y={tm_y}")

    station = get_nearest_station(tm_x, tm_y)
    if not station:
        print("[⚠️] 근처 측정소를 찾을 수 없습니다.")
        return

    print(f"✅ 가장 가까운 측정소: {station}")

    air = get_air_quality(station)
    if not air:
        print("[⚠️] 대기질 데이터를 불러오지 못했습니다.")
        return

    print(f"\n📊 [대기질 정보 - {station}]")
    print(f"- 측정시간: {air['dataTime']}")
    print(f"- 미세먼지(PM10): {air['pm10Value']} ㎍/㎥ ({grade_to_text(air.get('pm10Grade'))})")
    print(f"- 초미세먼지(PM2.5): {air['pm25Value']} ㎍/㎥ ({grade_to_text(air.get('pm25Grade'))})")
    print(f"- 오존(O3): {air['o3Value']} ppm ({grade_to_text(air.get('o3Grade'))})")

# ✅ 사용자 입력
if __name__ == "__main__":
    dong_input = input("조회할 동 이름을 입력하세요 (예: 용운동): ").strip()
    run_air_quality_flow(dong_input)
