import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import re
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import math

# ✅ 한글 폰트 설정 (윈도우 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 설정
APT_FILE = "아파트방향_주소_아파트명_최종_정제.csv"
FLASK_URL = "http://localhost:5000/weather"  # Flask 서버 주소

# ✅ 사용자 입력
APT_NAME = input("▶ 아파트명을 입력하세요 (예: e편한세상 둔산 102동): ").strip()
FLOOR_INPUT = input("▶ 층수를 입력하세요 (예: 10): ").strip()

try:
    floor_info = int(FLOOR_INPUT)
    height = floor_info * 3  # 1층 = 3m 가정
except ValueError:
    raise ValueError("❗ 숫자로 된 층수를 정확히 입력해주세요.")

# ✅ 아파트 정보 로딩
df = pd.read_csv(APT_FILE, on_bad_lines='skip')
df.columns = df.columns.str.replace(r"\(.*\)", "", regex=True).str.strip()
row = df[df["아파트명"] == APT_NAME]
if row.empty:
    raise ValueError(f"[❗오류] '{APT_NAME}' 아파트 정보를 찾을 수 없습니다.")

lat = row.iloc[0]["위도"]
lon = row.iloc[0]["경도"]
direction_text = row.iloc[0]["방향"]
address = row.iloc[0]["주소"]

# ✅ 동 추출
match = re.search(r"(\S+동)", address)
dong_name = match.group(1) if match else None
if dong_name is None:
    raise ValueError("❗ 주소에서 동 정보를 추출할 수 없습니다.")

# ✅ Flask API로 날씨 데이터 요청
response = requests.get(f"{FLASK_URL}?dong={dong_name}")
weather_json = response.json()
forecast_list = weather_json.get("forecast", [])
if not forecast_list:
    raise ValueError(f"[❗오류] '{dong_name}' 날씨 데이터를 받아오지 못했습니다.")

# ✅ 방향 → 도 단위 변환
def direction_to_degree(text):
    mapping = {
        "정남향": 180, "남향": 180, "남서향": 225,
        "서향": 270, "남동향": 135,
        "동향": 90, "북향": 0, "북서향": 315, "북동향": 45
    }
    return mapping.get(text.strip(), 180)

def adjust_radiation_by_direction(radiation, azimuth, facing_deg):
    delta = abs(azimuth - facing_deg)
    delta = min(delta, 360 - delta)
    weight = max(math.cos(math.radians(delta)), 0)
    return round(radiation * weight, 2)

# ✅ 일사량 계산
tz = pytz.timezone("Asia/Seoul")
today = datetime.now().date()
facing_deg = direction_to_degree(direction_text)

results = []
for entry in forecast_list[:6]:
    h, m = map(int, entry["time"].split(":"))
    dt = tz.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=h, minutes=m))

    alt = get_altitude(lat, lon, dt)
    azimuth = get_azimuth(lat, lon, dt)
    radiation = get_radiation_direct(dt, alt) if alt > 0 else 0
    adjusted_rad = adjust_radiation_by_direction(radiation, azimuth, facing_deg)

    results.append({
        "시간": f"{h}:{str(m).zfill(2)}",
        "고도": round(alt, 2),
        "방위각": round(azimuth, 2),
        "일사량(W/m²)": round(radiation, 2),
        "보정일사량": adjusted_rad,
        "기온(℃)": entry.get("temp_C", "?"),
        "습도(%)": entry.get("humidity_%", "?"),
        "풍속(m/s)": entry.get("wind_speed_mps", "?"),
        "하늘상태": entry.get("sky", "?"),
        "강수형태": entry.get("rain_type", "?")
    })

# ✅ 시각화
x = [r["시간"] for r in results]
y = [r["보정일사량"] for r in results]

plt.figure(figsize=(10, 5))
plt.plot(x, y, marker='o', label="보정 일사량(W/m²)")
plt.title(f"{APT_NAME} ({direction_text}, {floor_info}층 약 {height}m) | 보정 일사량 예측")
plt.xlabel("시간")
plt.ylabel("일사량 (W/m²)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ✅ 결과 출력
print(f"\n📍 위치: {lat}, {lon} | 방향: {direction_text} | 동: {dong_name} | 층수: {floor_info}층 ≈ {height}m\n")
print(pd.DataFrame(results))
