import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import numpy as np
import re

# ✅ 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 설정
CSV_FILE = "아파트방향_주소_아파트명_최종_정제.csv"
COORD_FILE = "좌표목록.csv"
KMA_API_KEY = "DIdS2JmzSt6HUtiZs2re8g"

# ✅ 사용자 입력
APT_NAME = input("▶ 아파트명을 입력하세요: ").strip()

# ✅ 아파트 정보 불러오기
df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
df.columns = df.columns.str.replace(r"\(.*\)", "", regex=True).str.strip()
row = df[df["아파트명"] == APT_NAME]
if row.empty:
    raise ValueError(f"[오류] '{APT_NAME}' 아파트 정보를 찾을 수 없습니다.")

lat = row.iloc[0]["위도"]
lon = row.iloc[0]["경도"]
direction = row.iloc[0]["방향"]
address = row.iloc[0]["주소"]

# ✅ 주소에서 동 이름 추출
match = re.search(r"(\S+동)", address)
if match:
    dong_name = match.group(1)
else:
    raise ValueError("❗ 주소에서 동 정보를 추출할 수 없습니다.")

print(f"📍 위치: {lat}, {lon} | 방향: {direction} | 동: {dong_name}")

# ✅ 방위각 계산 함수
def get_direction_angle(direction_str):
    mapping = {
        "동향": 90, "남동향": 135, "남향": 180, "남서향": 225,
        "서향": 270, "북서향": 315, "북향": 0, "북동향": 45
    }
    return mapping.get(direction_str.strip(), 180)

def correction_factor(sun_azimuth, apt_azimuth):
    diff = abs(sun_azimuth - apt_azimuth)
    diff = min(diff, 360 - diff)
    if diff > 90:
        return 0
    return np.cos(np.radians(diff))

# ✅ 기준 시각 계산
now = datetime.now()
base_date = now.strftime("%Y%m%d")
if now.minute < 45:
    base_time = (now - timedelta(hours=1)).strftime("%H30")
else:
    base_time = now.strftime("%H30")

# ✅ 날씨 API 호출
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

# ✅ 날씨 정보 조회
forecast = get_weather_forecast(dong_name)
times = sorted(forecast.keys())[:6]

# ✅ 일사량 계산
tz = pytz.timezone("Asia/Seoul")
today = now.date()
apt_azimuth = get_direction_angle(direction)
results = []

for t in times:
    h, m = int(t[:2]), int(t[2:])
    dt = tz.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=h, minutes=m))

    alt = get_altitude(lat, lon, dt)
    azi = get_azimuth(lat, lon, dt)
    raw_rad = get_radiation_direct(dt, alt) if alt > 0 else 0
    factor = correction_factor(azi, apt_azimuth)
    corrected_rad = raw_rad * factor

    weather = forecast[t]
    results.append({
        "시간": f"{h}:{str(m).zfill(2)}",
        "고도(°)": round(alt, 2),
        "방위각(°)": round(azi, 2),
        "보정 전 일사량(W/m²)": round(raw_rad, 2),
        "보정 계수": round(factor, 2),
        "보정 후 일사량(W/m²)": round(corrected_rad, 2),
        "기온(℃)": weather.get("T1H", "?"),
        "습도(%)": weather.get("REH", "?"),
        "풍속(m/s)": weather.get("WSD", "?"),
        "하늘상태": {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(weather.get("SKY", ""), "?"),
        "강수형태": {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(weather.get("PTY", ""), "?")
    })

# ✅ 결과 시각화
df_result = pd.DataFrame(results)
plt.figure(figsize=(10, 5))
plt.plot(df_result["시간"], df_result["보정 전 일사량(W/m²)"], marker='o', label="직달 일사량")
plt.plot(df_result["시간"], df_result["보정 후 일사량(W/m²)"], marker='s', label="보정 후 일사량")
plt.title(f"{APT_NAME} - 방향 보정 일사량 및 날씨")
plt.xlabel("시간")
plt.ylabel("일사량 (W/m²)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ✅ 출력
print(df_result)
