import cx_Oracle
import numpy as np
import pytz
from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
import requests
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

app = Flask(__name__)

# DB/API 설정
conn_info = {
    "user": "ef",
    "password": "ef",
    "dsn": cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
}
KMA_API_KEY = "DIdS2JmzSt6HUtiZs2re8g"
AIR_SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="
EXCEL_AIR = "tm_coords_from_api.csv"

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 아파트명 검색 (중복 없이)
@app.route("/search_apartment")
def search_apartment():
    word = request.args.get("q", "").strip()
    if not word:
        return jsonify([])
    conn = cx_Oracle.connect(**conn_info)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT KAPT_NAME, KAPT_CODE
        FROM APARTMENTS_ADDRESS
        WHERE KAPT_NAME LIKE '%' || :1 || '%'
        ORDER BY KAPT_NAME
        FETCH FIRST 20 ROWS ONLY
    """, (word,))
    rows = cur.fetchall()
    conn.close()
    seen = set()
    res = []
    for name, code in rows:
        if name not in seen:
            res.append({"code": code, "name": name})
            seen.add(name)
    return jsonify(res)

# 2. 아파트 동/블록 선택 + dong(법정동명) 포함
@app.route("/get_blocks")
def get_blocks():
    code = request.args.get("kapt_code", "").strip()
    if not code:
        return jsonify([])
    conn = cx_Oracle.connect(**conn_info)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.APT_BLOCK, b.DIRECTION, b.LATITUDE, b.LONGITUDE, a.DONG
        FROM APARTMENTS_BLOCK b
        JOIN APARTMENTS_ADDRESS a ON b.KAPT_CODE = a.KAPT_CODE
        WHERE b.KAPT_CODE = :1
        ORDER BY b.APT_BLOCK
    """, (code,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([
        {
            "block": r[0],
            "direction": r[1],
            "lat": float(r[2]),
            "lon": float(r[3]),
            "dong": r[4]
        } for r in rows
    ])

# 격자 변환, 날씨, 미세먼지 함수 생략(위 내용 그대로 사용)
def latlon_to_xy(lat, lon):
    import math
    RE = 6371.00877; GRID = 5.0
    SLAT1 = 30.0; SLAT2 = 60.0; OLON = 126.0; OLAT = 38.0; XO = 43; YO = 136
    DEGRAD = math.pi / 180.0
    re = RE / GRID; slat1 = SLAT1 * DEGRAD; slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD; olat = OLAT * DEGRAD
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn
    x = ra * math.sin(theta) + XO + 0.5
    y = ro - ra * math.cos(theta) + YO + 0.5
    return int(x), int(y)

def get_weather_forecast(lat, lon):
    nx, ny = latlon_to_xy(lat, lon)
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    base_time = (now - timedelta(hours=1)).strftime("%H30") if now.minute < 45 else now.strftime("%H30")
    url = (
        f"https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON&base_date={base_date}&base_time={base_time}"
        f"&nx={nx}&ny={ny}&authKey={KMA_API_KEY}"
    )
    response = requests.get(url)
    items = response.json()["response"]["body"]["items"]["item"]
    forecast = {}
    for item in items:
        t, cat, val = item["fcstTime"], item["category"], item["fcstValue"]
        if t not in forecast:
            forecast[t] = {}
        forecast[t][cat] = val
    return forecast

def get_air_quality(dong_name):
    try:
        df = pd.read_csv(EXCEL_AIR)
        row = df[df["3단계"] == dong_name]
        if row.empty:
            return None
        tm_x, tm_y = row.iloc[0]["TM_X"], row.iloc[0]["TM_Y"]
        station_res = requests.get(
            "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList",
            params={
                "tmX": tm_x, "tmY": tm_y, "returnType": "json",
                "serviceKey": AIR_SERVICE_KEY, "ver": "1.1"
            }
        )
        station_data = station_res.json()
        station_list = station_data.get("response", {}).get("body", {}).get("items", [])
        if not station_list:
            return None
        station = station_list[0]["stationName"]
        air_res = requests.get(
            "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty",
            params={
                "stationName": station, "returnType": "json",
                "serviceKey": AIR_SERVICE_KEY, "dataTerm": "DAILY", "ver": "1.3"
            }
        )
        air_data = air_res.json()
        items = air_data.get("response", {}).get("body", {}).get("items", [])
        if not items:
            return None
        item = items[0]
        def grade_text(code):
            return {"1": "좋음", "2": "보통", "3": "나쁨", "4": "매우나쁨"}.get(str(code), "-")
        return {
            "station": station,
            "time": item.get("dataTime"),
            "PM10": f"{item.get('pm10Value')} ㎍/㎥ ({grade_text(item.get('pm10Grade'))})",
            "PM2.5": f"{item.get('pm25Value')} ㎍/㎥ ({grade_text(item.get('pm25Grade'))})",
            "O3": f"{item.get('o3Value')} ppm ({grade_text(item.get('o3Grade'))})",
            "pm10_val": float(item.get('pm10Value') or 0),
            "pm25_val": float(item.get('pm25Value') or 0)
        }
    except Exception as e:
        return None

def get_direction_angle(direction_str):
    mapping = {
        "동향": 90, "남동향": 135, "남향": 180, "남서향": 225,
        "서향": 270, "북서향": 315, "북향": 0, "북동향": 45
    }
    return mapping.get(direction_str.strip(), 180)

def correction_factor(sun_azimuth, apt_azimuth):
    diff = abs(sun_azimuth - apt_azimuth)
    diff = min(diff, 360 - diff)
    if diff <= 60:
        return max(0, np.cos(np.radians(diff)))
    elif diff <= 150:
        decay = 0.5 ** ((diff - 60) / 30)
        return decay * 0.8
    else:
        return 0

def get_dry_label(val):
    if val < 80: return "매우 낮음"
    elif val < 150: return "낮음"
    elif val < 220: return "적합"
    else: return "매우 적합"

# ★ 엣지(Edge) 가중치: 해가 뜨고 지는 시간에서만 층수 효과
def edge_boost(hour, floor, edge_range=2, boost=0.2):
    # edge_range: 몇 시간 범위에서 적용할지 (예: 4~6, 18~20시)
    # boost: 층당 가중치
    if hour <= 4 + edge_range:  # 일출 ~ edge 구간
        return 1 + (floor - 1) * boost * (edge_range - (hour - 4)) / edge_range
    elif hour >= 20 - edge_range:  # 일몰 직전 ~ edge 구간
        return 1 + (floor - 1) * boost * (edge_range - (20 - hour)) / edge_range
    else:
        return 1

@app.route("/analyze_solar", methods=["POST"])
def analyze_solar():
    data = request.get_json()
    apt_code = data.get("apt_code")
    block = data.get("block")
    floor = int(data.get("floor"))
    direction = data.get("direction")
    dong_name = data.get("dong")

    conn = cx_Oracle.connect(**conn_info)
    cur = conn.cursor()
    cur.execute("""
        SELECT LATITUDE, LONGITUDE
        FROM APARTMENTS_BLOCK
        WHERE KAPT_CODE = :1 AND APT_BLOCK = :2
    """, (apt_code, block))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"message": "위치 정보를 찾을 수 없습니다."})
    lat, lon = float(row[0]), float(row[1])
    apt_azimuth = get_direction_angle(direction)

    forecast = get_weather_forecast(lat, lon)
    forecast_times = set(forecast.keys())
    air_quality = get_air_quality(dong_name)
    pm10_val = air_quality["pm10_val"] if air_quality else None
    pm25_val = air_quality["pm25_val"] if air_quality else None

    tz = pytz.timezone("Asia/Seoul")
    today = datetime.now().date()
    height = floor * 3

    results = []
    for h in range(4, 21):  # 4~20시, 1시간 간격
        m = 0
        dt = tz.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=h, minutes=m))
        alt = get_altitude(lat, lon, dt)
        azi = get_azimuth(lat, lon, dt)
        raw_rad = get_radiation_direct(dt, alt) if alt > 0 else 0
        attenuation = np.exp(-0.004 * height)
        attenuated = raw_rad * attenuation
        angle_factor = correction_factor(azi, apt_azimuth)
        final_rad = attenuated * angle_factor

        # 엣지(Edge) 효과 (아침·저녁에만 적용)
        if raw_rad > 0:
            final_rad *= edge_boost(h, floor, edge_range=2, boost=0.2)

        t_str = f"{str(h).zfill(2)}{str(m).zfill(2)}"
        weather = {}
        # 날씨 보정
        if t_str in forecast_times:
            weather = forecast[t_str]
            sky = weather.get("SKY", "")
            pty = weather.get("PTY", "")
            if pty != "0":
                final_rad = 0
            elif sky == "4":
                final_rad *= 0.6
            elif sky == "3":
                final_rad *= 0.9

        # 미세먼지 보정
        if pm10_val is not None and pm10_val > 80:
            final_rad *= 0.9
        if pm10_val is not None and pm10_val > 100:
            final_rad *= 0.8
        if pm25_val is not None and pm25_val > 35:
            final_rad *= 0.9
        if pm25_val is not None and pm25_val > 50:
            final_rad *= 0.8

        results.append({
            "시간": f"{h}:{str(m).zfill(2)}",
            "기본 일사량": round(raw_rad, 2),
            "고도 보정": round(attenuated, 2),
            "최종 보정 일사량": round(final_rad, 2),
            "건조 적합도": get_dry_label(final_rad),
            "기온(℃)": weather.get("T1H", "?"),
            "습도(%)": weather.get("REH", "?"),
            "풍속(m/s)": weather.get("WSD", "?"),
            "하늘": {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(weather.get("SKY", ""), "?"),
            "강수": {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(weather.get("PTY", ""), "?")
        })

    # ---- 결과 표 ----
    message = "시간\t기본 일사량\t고도 보정\t최종 보정 일사량\t건조 적합도\n"
    for r in results:
        message += f"{r['시간']}\t{r['기본 일사량']}\t{r['고도 보정']}\t{r['최종 보정 일사량']}\t{r['건조 적합도']}\n"

    # ---- 날씨 예보 표(예보 있는 시간만) ----
    weather_message = "시간\t기온(℃)\t습도(%)\t풍속(m/s)\t하늘\t강수\n"
    for r in results:
        if r["기온(℃)"] != "?":
            weather_message += f"{r['시간']}\t{r['기온(℃)']}\t{r['습도(%)']}\t{r['풍속(m/s)']}\t{r['하늘']}\t{r['강수']}\n"

    # ---- 대기질 표 ----
    air_message = ""
    if air_quality:
        air_message += f"[대기질] {air_quality['station']}({air_quality['time']}) PM10: {air_quality['PM10']}, PM2.5: {air_quality['PM2.5']}, O3: {air_quality['O3']}\n"

    # ---- 그래프 ----
    plt.figure(figsize=(13, 5))
    xs = [r["시간"] for r in results]
    plt.plot(xs, [r["기본 일사량"] for r in results], marker='o', label="기본 일사량")
    plt.plot(xs, [r["고도 보정"] for r in results], marker='^', label="고도 보정 일사량")
    plt.plot(xs, [r["최종 보정 일사량"] for r in results], marker='s', label="최종 보정 일사량")
    for x, y, label in zip(xs, [r["최종 보정 일사량"] for r in results], [r["건조 적합도"] for r in results]):
        plt.text(x, y + 10, label, ha='center', fontsize=9, color='blue')
    plt.xticks(rotation=45)
    plt.title(f"{block} {floor}층 {direction} - 4~20시(1시간 간격) 일사량/건조 적합도")
    plt.xlabel("시간")
    plt.ylabel("일사량 (W/m²)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    img_url = f"data:image/png;base64,{img_base64}"

    return jsonify({
        "message": message,
        "img_url": img_url,
        "weather_message": weather_message,
        "air_message": air_message,
        "air_quality": air_quality
    })

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)