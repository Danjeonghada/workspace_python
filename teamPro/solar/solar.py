import pandas as pd
import math
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct

# ✅ 1. CSV 파일 읽기
df = pd.read_csv("아파트방향.csv")
df.columns = df.columns.str.strip()  # 공백 제거

# ✅ 2. 방향 → 방위각 변환 (기본값은 남향 처리)
azimuth_map = {
    "남향": 180,
    "남동향": 135,
    "남서향": 225,
    "동향": 90,
    "서향": 270,
    "북향": 0,
}

# ✅ 3. 시간 설정 (UTC + timezone-aware)
date = datetime.utcnow().replace(tzinfo=pytz.utc)

# ✅ 4. 결과 저장 리스트
results = []

for i, row in df.iterrows():
    try:
        lat = float(row["위도"])
        lon = float(row["경도"])
        direction = row["방향"].strip()
        apt_name = row["아파트명"].strip()

        surface_azimuth = azimuth_map.get(direction)
        if surface_azimuth is None:
            continue  # 등록되지 않은 방향은 제외

        # 태양 위치 계산
        sun_alt = get_altitude(lat, lon, date)
        sun_az = get_azimuth(lat, lon, date)

        # 일사량 계산 (고도는 50m로 고정)
        irradiance = get_radiation_direct(date, sun_alt, 50)
        angle_diff = math.radians(abs(sun_az - surface_azimuth))
        adjusted_irr = irradiance * max(math.cos(angle_diff), 0)

        results.append({
            "아파트명": apt_name,
            "방향": direction,
            "태양 방위각": round(sun_az, 2),
            "태양 고도각": round(sun_alt, 2),
            "직달 일사량(W/m²)": round(irradiance, 2),
            "창에 도달 일사량(W/m²)": round(adjusted_irr, 2)
        })

    except Exception as e:
        print(f"[에러] {i}번째 행 처리 실패: {e}")

# ✅ 5. 결과 DataFrame 생성 및 저장
result_df = pd.DataFrame(results)
result_df.to_csv("일사량결과.csv", index=False)
print("✅ 저장 완료: 일사량결과.csv")

# ✅ 6. 시각화 (막대 그래프)
plt.figure(figsize=(12, 6))
plt.bar(result_df["아파트명"], result_df["창에 도달 일사량(W/m²)"])
plt.xticks(rotation=90)
plt.xlabel("아파트명")
plt.ylabel("도달 일사량 (W/m²)")
plt.title("아파트 방향별 도달 일사량 (현재시간 기준)")
plt.tight_layout()
plt.savefig("일사량그래프.png", dpi=300)
plt.show()
