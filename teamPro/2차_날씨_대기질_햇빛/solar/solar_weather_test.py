import pandas as pd
from datetime import datetime, timedelta
import pytz
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import numpy as np

# ✅ 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 아파트 정보
APT_NAME = "e편한세상 둔산 102동"
LAT, LON = 36.342582, 127.39299
APT_DIRECTION = "남서향"

# ✅ 방향 문자열 → 방위각(도) 변환
def get_direction_angle(direction_str):
    mapping = {
        "동향": 90, "남동향": 135, "남향": 180, "남서향": 225,
        "서향": 270, "북서향": 315, "북향": 0, "북동향": 45
    }
    return mapping.get(direction_str.strip(), 180)

# ✅ 태양과 방향의 각도 차이에 따른 보정 계수
def correction_factor(sun_azimuth, apt_azimuth):
    diff = abs(sun_azimuth - apt_azimuth)
    diff = min(diff, 360 - diff)
    if diff > 90:
        return 0
    return np.cos(np.radians(diff))

# ✅ 6시간 시간대 생성
now = datetime.now()
tz = pytz.timezone("Asia/Seoul")
today = now.date()
base_hour = now.hour if now.minute >= 45 else now.hour - 1
times = [tz.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=base_hour + i)) for i in range(6)]

# ✅ 일사량 계산
apt_azimuth = get_direction_angle(APT_DIRECTION)
results = []

for dt in times:
    hour = dt.hour
    alt = get_altitude(LAT, LON, dt)
    azi = get_azimuth(LAT, LON, dt)
    raw_rad = get_radiation_direct(dt, alt) if alt > 0 else 0
    factor = correction_factor(azi, apt_azimuth)
    corrected_rad = raw_rad * factor

    results.append({
        "시간": f"{hour}:00",
        "고도(°)": round(alt, 2),
        "방위각(°)": round(azi, 2),
        "보정 전 일사량(W/m²)": round(raw_rad, 2),
        "보정 후 일사량(W/m²)": round(corrected_rad, 2),
        "보정 계수": round(factor, 2)
    })

# ✅ 시각화
df_result = pd.DataFrame(results)
plt.figure(figsize=(10, 5))
plt.plot(df_result["시간"], df_result["보정 전 일사량(W/m²)"], marker='o', label="직달 일사량")
plt.plot(df_result["시간"], df_result["보정 후 일사량(W/m²)"], marker='s', label="보정 후 일사량")
plt.title(f"{APT_NAME} - 방향 보정 일사량")
plt.xlabel("시간")
plt.ylabel("일사량 (W/m²)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
print(df_result)
