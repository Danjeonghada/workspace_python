from datetime import datetime, timedelta
import pytz
from pysolar.solar import get_altitude
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# ✅ 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 위치 설정: 대전 e편한세상 둔산 102동
latitude = 36.342582
longitude = 127.392990

# 날짜 설정: 하지(태양 고도 가장 높은 날)
date = datetime(2025, 6, 21)
tz = pytz.timezone("Asia/Seoul")

# 오전 5시 ~ 오후 8시 (태양 떠있는 시간대 기준)
times = [tz.localize(date + timedelta(hours=h)) for h in range(5, 20)]

# 태양 고도 및 일사량 계산
altitudes = [get_altitude(latitude, longitude, t) for t in times]
radiations = [get_radiation_direct(t, alt) if alt > 0 else 0 for t, alt in zip(times, altitudes)]

# 시각화
plt.figure(figsize=(10, 5))
plt.plot([t.hour for t in times], radiations, marker='o', label='직달 일사량 (W/m²)')
plt.title('e편한세상 둔산 102동 - 2025년 6월 21일 시간대별 일사량')
plt.xlabel('시간 (시)')
plt.ylabel('일사량 (W/m²)')
plt.grid(True)
plt.xticks(range(5, 20))
plt.legend()
plt.tight_layout()
plt.show()
