import pandas as pd
import requests
from pyproj import Transformer

# ✅ TM 좌표 변환 캐시
tm_cache = {}

# ✅ WGS84 → TM 변환 함수
def wgs84_to_tm(lat, lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:2097", always_xy=True)
    return transformer.transform(lon, lat)

# ✅ 캐시 활용한 TM 좌표 계산
def get_tm_coords(lat, lon):
    key = (lat, lon)
    if key in tm_cache:
        return tm_cache[key]
    tm_x, tm_y = wgs84_to_tm(lat, lon)
    tm_cache[key] = (tm_x, tm_y)
    return tm_x, tm_y

# ✅ 엑셀에서 위도/경도 추출
def get_latlon_from_dong(dong_name, excel_path="xy_code_daejeon.xlsx"):
    df = pd.read_excel(excel_path)
    row = df[df['3단계'] == dong_name]
    if row.empty:
        print(f"[❌] '{dong_name}' 동을 엑셀에서 찾을 수 없습니다.")
        return None
    lat = float(row.iloc[0]['위도(초/100)'])
    lon = float(row.iloc[0]['경도(초/100)'])
    return lat, lon

# ✅ TM 좌표 → 가장 가까운 측정소
def get_nearest_station(tm_x, tm_y, service_key):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList"
    params = {
        "tmX": tm_x,
        "tmY": tm_y,
        "returnType": "json",
        "serviceKey": service_key,
        "ver": "1.1"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        items = data.get('response', {}).get('body', {}).get('items', [])
        if not items:
            print("[❌] 측정소 정보가 없습니다.")
            return None
        return items[0]['stationName']
    except Exception as e:
        print(f"[❌] 측정소 API 오류: {e}")
        return None

# ✅ 숫자 등급 → 텍스트
def grade_to_text(code):
    return {
        "1": "좋음",
        "2": "보통",
        "3": "나쁨",
        "4": "매우나쁨"
    }.get(str(code), "-")

# ✅ 측정소 → 대기질 출력
def print_air_quality(station_name, service_key):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {
        "stationName": station_name,
        "returnType": "json",
        "serviceKey": service_key,
        "dataTerm": "DAILY",
        "ver": "1.3"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        items = data.get('response', {}).get('body', {}).get('items', [])
        if not items:
            print(f"[❌] '{station_name}' 측정소 대기질 정보가 없습니다.")
            return

        latest = items[0]
        print(f"\n📍 [{station_name}] 측정소 대기질 정보")
        print(f"- 측정시간: {latest['dataTime']}")
        print(f"- 미세먼지(PM10): {latest['pm10Value']} ㎍/㎥ ({grade_to_text(latest.get('pm10Grade'))})")
        print(f"- 초미세먼지(PM2.5): {latest['pm25Value']} ㎍/㎥ ({grade_to_text(latest.get('pm25Grade'))})")
        print(f"- 오존(O3): {latest['o3Value']} ppm ({grade_to_text(latest.get('o3Grade'))})")
    except Exception as e:
        print(f"[❌] 대기질 API 오류: {e}")

# ✅ 전체 실행 함수
def show_air_quality_from_dong(dong_name, service_key):
    latlon = get_latlon_from_dong(dong_name)
    if not latlon:
        return
    lat, lon = latlon
    tm_x, tm_y = get_tm_coords(lat, lon)
    station = get_nearest_station(tm_x, tm_y, service_key)
    if station:
        print(f"\n✅ '{dong_name}' 기준 가장 가까운 측정소는 → {station}")
        print_air_quality(station, service_key)

# ✅ 실행 예시
if __name__ == "__main__":
    # ❗ 디코딩된 서비스 키 사용 (슬래시 포함된 형태)
    SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="
    show_air_quality_from_dong("용운동", SERVICE_KEY)
