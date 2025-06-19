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
COORD_FILE = "좌표목록.csv"
KMA_API_KEY = "DIdS2JmzSt6HUtiZs2re8g"

# ✅ 사용자 입력
APT_NAME = input("▶ 아파트명을 입력하세요 (예: e편한세상 둔산 102동): ").strip()
FLOOR_INPUT = input("▶ 몇 층인지 입력하세요 (예: 10): ").strip()

# 층수 → 높이 계산 (1층당 3m)
try:
    floor_info = int(FLOOR_INPUT)
    height = floor_info * 3
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

# ✅ 기준 시각 계산
now = datetime.now()
base_date = now.strftime("%Y%m%d")
base_time = (now - timedelta(hours=1)).strftime("%H30") if now.minute < 45 else now.strftime("%H30")

# ✅ 날씨 API 함수
def get_weather_forecast(dong_name):
    coord_df = pd.read_csv(COORD_FILE)
    r = coord_df[coord_df["3단계"] == dong_name]
    if r.empty:
        raise ValueError(f"[좌표오류] '{dong_name}' 격자 좌표를 찾을 수 없습니다.")
    nx, ny = int(r.iloc[0]["격자 X"]), int(r.iloc[0]["격자 Y"])

    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON&base_date={base_date}&base_time={base_time}"
        f"&nx={nx}&ny={ny}&authKey={KMA_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    items = data["response"]["body"]["items"]["item"]

    forecast = {}
    for item in items:
        time = item["fcstTime"]
        cat = item["category"]
        val = item["fcstValue"]
        if time not in forecast:
            forecast[time] = {}
        forecast[time][cat] = val
    return forecast

# ✅ 방향각 계산 및 보정
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

# ✅ 예보 및 일사량 계산
forecast = get_weather_forecast(dong_name)
times = sorted(forecast.keys())[:6]
tz = pytz.timezone("Asia/Seoul")
today = datetime.now().date()
facing_deg = direction_to_degree(direction_text)

results = []
for t in times:
    h, m = int(t[:2]), int(t[2:])
    dt = tz.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=h, minutes=m))

    alt = get_altitude(lat, lon, dt)
    azimuth = get_azimuth(lat, lon, dt)
    radiation = get_radiation_direct(dt, alt) if alt > 0 else 0
    adjusted_rad = adjust_radiation_by_direction(radiation, azimuth, facing_deg)

    weather = forecast[t]
    results.append({
        "시간": f"{h}:{str(m).zfill(2)}",
        "고도": round(alt, 2),
        "방위각": round(azimuth, 2),
        "일사량(W/m²)": round(radiation, 2),
        "보정일사량": adjusted_rad,
        "기온(℃)": weather.get("T1H", "?"),
        "습도(%)": weather.get("REH", "?"),
        "풍속(m/s)": weather.get("WSD", "?"),
        "하늘상태": {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(weather.get("SKY", ""), "?"),
        "강수형태": {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(weather.get("PTY", ""), "?")
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

# ✅ 출력
print(f"\n📍 위치: {lat}, {lon} | 방향: {direction_text} | 동: {dong_name} | 층수: {floor_info}층 ≈ {height}m\n")
print(pd.DataFrame(results))

