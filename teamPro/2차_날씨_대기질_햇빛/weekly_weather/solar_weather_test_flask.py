import cx_Oracle
import numpy as np
import pytz
from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta, time
import requests
from pysolar.solar import get_altitude, get_azimuth
from pysolar.radiation import get_radiation_direct
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# DB/API 설정
conn_info = {
    "user": "ef",
    "password": "ef",
    "dsn": cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
}
KMA_API_KEY = "vOoxqLD1QaWqMaiw9bGlig"
AIR_SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

# Matplotlib 백엔드 설정 추가
import matplotlib

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def is_dust_good(grade):
    # '좋음', '보통'이면 True, '나쁨', '매우나쁨'이면 False
    return grade in ["좋음", "보통"]

def get_latest_daejeon_forecasts():
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth"
    params = {
        'serviceKey': AIR_SERVICE_KEY,
        'returnType': 'json',
        'searchDate': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'ver': '1.1'
    }
    res = requests.get(url, params=params, timeout=8)
    data = res.json()
    items = (
        data.get('response', {})
            .get('body', {})
            .get('items', [])
    )
    code_map = {'PM10': '미세먼지(PM10)', 'PM25': '초미세먼지(PM2.5)', 'O3': '오존(O3)'}
    result = []
    for item in items:
        code = item.get('informCode')
        if code not in code_map:
            continue
        date = item.get('informData')  # 예보일
        # 대전 등급 추출
        grade = '-'
        grade_text = item.get('informGrade', '')
        for region_part in grade_text.split(','):
            region_part = region_part.strip()
            if region_part.startswith("대전"):
                parts = region_part.split(":")
                if len(parts) > 1:
                    grade = parts[1].strip()
        desc = item.get('informCause', '')  # 예보설명
        announce_time = item.get('dataTime', '')  # 발표시각
        result.append({
            "예보종류": code_map[code],
            "예보일": date,
            "예보등급": grade,
            "발표시각": announce_time,
            "예보설명": desc
        })
    # 날짜/종류별로 "발표시각" 최신 1개만 남김
    df = pd.DataFrame(result)
    df = df.sort_values(by=["예보일", "예보종류", "발표시각"], ascending=[True, True, False])
    df = df.drop_duplicates(subset=["예보일", "예보종류"], keep="first").reset_index(drop=True)
    return df

# --- [여기부터 추가: 등급 함수] ---
def get_temp_grade(temp):
    temp = float(temp)
    if temp < -5: return "매우 부적합", "저체온·동상 위험"
    if temp < 5: return "부적합", "실내온도 급강하 위험"
    if temp < 10: return "다소 부적합", "쌀쌀, 일부 시간만 권장"
    if temp < 18: return "적합", "환기에 적당한 온도"
    if temp < 25: return "매우 적합", "쾌적, 이상적 환기 온도"
    if temp < 30: return "다소 부적합", "실내 불쾌지수 상승 우려"
    if temp < 35: return "부적합", "더운 공기 유입"
    return "매우 부적합", "열사병 위험, 절대 환기 금지"

def get_humi_grade(humi):
    humi = float(humi)
    if humi < 30: return "매우 부적합", "점막 건조, 바이러스 확산 위험"
    if humi < 40: return "부적합", "건조함, 피부·호흡기 불쾌감"
    if humi < 61: return "매우 적합", "이상적 쾌적 습도 범위"
    if humi < 81: return "다소 부적합", "다소 습함, 불쾌지수 약간 상승"
    return "부적합", "곰팡이 등 미생물 번식 위험"

def get_wind_grade(wind):
    wind = float(wind)
    if wind < 0.5: return "매우 부적합", "거의 무풍, 환기 효과 없음"
    if wind < 1.0: return "부적합", "약한 바람, 실질적 효과 부족"
    if wind < 3.1: return "매우 적합", "환기에 가장 적합한 풍속"
    return "다소 부적합", "강풍, 외풍 유입 주의"

# 1. 아파트명 검색
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


def latlon_to_xy(lat, lon):
    import math
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136
    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
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


# 실황 요청 (각 시간별로 가장 가까운 과거 10분 단위 데이터)
def get_ultra_srt_ncst(api_key, nx, ny, base_date, base_time):
    url = (
        f"https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey={api_key}"
    )
    items = []
    try:
        res = requests.get(url)
        items = res.json()["response"]["body"]["items"]["item"]
    except Exception:
        pass
    weather = {item["category"]: item["obsrValue"] for item in items}
    return weather


# 초단기예보(1시간 간격, 미래예측)
def get_ultra_forecast(lat, lon):
    nx, ny = latlon_to_xy(lat, lon)
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    # 이미지에서 본 것과 같이 40분 기준 대신 45분 기준으로 변경
    base_time = (now - timedelta(hours=1)).strftime("%H00") if now.minute < 45 else now.strftime("%H00")
    url = (
        f"https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON&base_date={base_date}&base_time={base_time}"
        f"&nx={nx}&ny={ny}&authKey={KMA_API_KEY}"
    )
    items = []
    try:
        res = requests.get(url)
        items = res.json()["response"]["body"]["items"]["item"]
    except Exception:
        pass
    fcst = {}
    for item in items:
        t = item["fcstTime"]
        if t not in fcst:
            fcst[t] = {}
        fcst[t][item["category"]] = item["fcstValue"]
    return fcst


# Helper function for air quality grades (already exists in original script)
def grade_text(code):
    return {"1": "좋음", "2": "보통", "3": "나쁨", "4": "매우나쁨"}.get(str(code), "-")


# Helper function for ventilation suitability (already exists in original script)
def get_ventilation_suitability(param_name, value, grade_code):
    # 미세먼지 (PM10)
    if param_name == "PM10":
        if grade_code == "1":  # 좋음
            return "적합"
        elif grade_code == "2":  # 보통
            return "적합"
        else:  # 나쁨 이상
            return "부적합"
    # 초미세먼지 (PM2.5)
    elif param_name == "PM2.5":
        if grade_code == "1":  # 좋음
            return "매우 적합"
        elif grade_code == "2":  # 보통
            return "적합"
        else:  # 나쁨 이상
            return "부적합"
    # 오존 (O3)
    elif param_name == "O3":
        if grade_code == "1":  # 좋음
            return "매우 적합"
        elif grade_code == "2":  # 보통
            return "매우 적합"  # 오존은 보통이어도 환기에는 적합하다고 판단 (외부 오염물질 유입 방지)
        else:  # 나쁨 이상
            return "부적합"
    return "-"


def get_air_quality(dong_name):
    conn = None  # Initialize conn
    try:
        conn = cx_Oracle.connect(**conn_info)
        cur = conn.cursor()

        # TM 좌표 기준 가까운 측정소 3개 조회 (사용자 요청에 따라 DB 사용)
        cur.execute("""
            SELECT *
            FROM (
                SELECT
                    t2.STATION_NAME,
                    MIN(t2.DONG_NAME) AS SAMPLE_DONG,
                    MIN(t2.TM_X) AS TM_X,
                    MIN(t2.TM_Y) AS TM_Y,
                    MIN(SQRT(POWER(t2.TM_X - t1.TM_X, 2) + POWER(t2.TM_Y - t1.TM_Y, 2))) AS DIST
                FROM DAEJEON_STATION_MAP t1
                JOIN DAEJEON_STATION_MAP t2
                    ON t2.STATION_NAME IS NOT NULL
                WHERE t1.DONG_NAME = :dong_name
                GROUP BY t2.STATION_NAME
            )
            ORDER BY DIST
            FETCH FIRST 3 ROWS ONLY
        """, (dong_name,))

        stations = [row[0] for row in cur.fetchall()]
        if not stations:
            print(f"[❌주변 측정소 없음] {dong_name}")
            return None

        # 관측소 하나씩 시도하여 데이터 가져오기
        for station in stations:
            try:
                air_res = requests.get(
                    "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty",
                    params={
                        "stationName": station,
                        "returnType": "json",
                        "serviceKey": AIR_SERVICE_KEY,
                        "dataTerm": "DAILY",
                        "ver": "1.3"
                    },
                    timeout=5  # Add timeout for robustness
                )
                items = air_res.json().get("response", {}).get("body", {}).get("items", [])
                if not items:
                    continue  # 데이터 없음, 다음 측정소로

                item = items[0]
                # pm10, pm25, o3가 모두 '-'면 유효하지 않은 데이터로 판단 (Original logic)
                if (item.get('pm10Value') == '-' and item.get('pm25Value') == '-' and item.get('o3Value') == '-'):
                    continue  # 다음 측정소로

                # Ensure values are float and handle '-' (Original logic, slightly improved for robustness)
                pm10_val_raw = item.get('pm10Value')
                pm10_val = float(pm10_val_raw) if pm10_val_raw and pm10_val_raw != '-' else 0.0

                pm25_val_raw = item.get('pm25Value')
                pm25_val = float(pm25_val_raw) if pm25_val_raw and pm25_val_raw != '-' else 0.0

                o3_val_raw = item.get('o3Value')
                o3_val = float(o3_val_raw) if o3_val_raw and o3_val_raw != '-' else 0.0

                print(station, '관측소')
                # Return structure matching the original get_air_quality's output,
                # including grade and suitability for 'analyze_solar' function.
                return {
                    "station": station,
                    "time": item.get("dataTime"),
                    "PM10_val": pm10_val_raw,  # Keep raw string for display
                    "PM10_grade": item.get('pm10Grade'),
                    "PM10_text": f"{pm10_val_raw} ㎍/㎥ ({grade_text(item.get('pm10Grade'))})",
                    "PM2.5_val": pm25_val_raw,  # Keep raw string for display
                    "PM2.5_grade": item.get('pm25Grade'),
                    "PM2.5_text": f"{pm25_val_raw} ㎍/㎥ ({grade_text(item.get('pm25Grade'))})",
                    "O3_val": o3_val_raw,  # Keep raw string for display
                    "O3_grade": item.get('o3Grade'),
                    "O3_text": f"{o3_val_raw} ppm ({grade_text(item.get('o3Grade'))})",
                    "pm10_val": pm10_val,  # Float for calculations
                    "pm25_val": pm25_val,  # Float for calculations
                    "ventilation_pm10": get_ventilation_suitability("PM10", pm10_val_raw, item.get('pm10Grade')),
                    "ventilation_pm25": get_ventilation_suitability("PM2.5", pm25_val_raw, item.get('pm25Grade')),
                    "ventilation_o3": get_ventilation_suitability("O3", o3_val_raw, item.get('o3Grade')),
                }

            except requests.exceptions.Timeout:
                print(f"[❌API 타임아웃] {station}")
                continue
            except Exception as e:
                print(f"[❌API 실패] {station}: {e}")
                continue

        print(f"[❌모든 시도 실패] {dong_name} 주변 측정소에서 유효한 데이터를 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"[❌DB/네트워크 오류] {dong_name}: {e}")
        return None
    finally:
        if conn:
            conn.close()


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
    if val < 80:
        return "매우 낮음"
    elif val < 150:
        return "낮음"
    elif val < 220:
        return "적합"
    else:
        return "매우 적합"


def edge_boost(hour, floor, edge_range=2, boost=0.2):
    if hour < 5 + edge_range:  # 일출 전후 (5~7시)
        edge = (5 + edge_range) - hour  # 예: hour=5면 2, hour=7이면 0
        return 1 + (floor - 1) * boost * (edge / edge_range)
    elif hour > 20 - edge_range:  # 일몰 전후 (18~20시)
        edge = hour - (20 - edge_range)  # 예: hour=18이면 0, hour=20이면 2
        return 1 + (floor - 1) * boost * (edge / edge_range)
    else:
        return 1

def get_vilage_fcst_all(lat, lon):
    nx, ny = latlon_to_xy(lat, lon)
    now = datetime.now()
    base_date, base_time = get_latest_base_time(now)
    max_retry = 5  # 최대 5번 fallback
    tries = 0

    while tries < max_retry:
        url = (
            f"https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"
            f"?pageNo=1&numOfRows=1000&dataType=JSON&base_date={base_date}&base_time={base_time}"
            f"&nx={nx}&ny={ny}&authKey={KMA_API_KEY}"
        )
        try:
            res = requests.get(url, timeout=7)
            items = res.json()["response"]["body"]["items"]["item"]
        except Exception:
            items = []
        if items:
            break
        # fallback (3시간 전으로)
        tries += 1
        base_hour = int(base_time[:2])
        base_hour -= 3
        if base_hour < 0:
            base_hour += 24
            dt = datetime.strptime(base_date, "%Y%m%d") - timedelta(days=1)
            base_date = dt.strftime("%Y%m%d")
        base_time = f"{base_hour:02d}00"

    # 시간별로 dict 정리 (예: '202407011100')
    fcst_dict = {}
    for item in items:
        dt = item["fcstDate"] + item["fcstTime"]
        if dt not in fcst_dict:
            fcst_dict[dt] = {}
        fcst_dict[dt][item["category"]] = item["fcstValue"]

    # 시간별 데이터 리스트로 변환 (정렬)
    result = []
    for key in sorted(fcst_dict.keys()):
        data = fcst_dict[key]
        temp = float(data.get("TMP", 0))
        humi = float(data.get("REH", 0))
        wind = float(data.get("WSD", 0))
        vec = data.get("VEC", "?")
        # ★ 환기 등급/사유 분석
        if temp != "?" and humi != "?" and wind != "?":
            vent_grade, vent_reason = analyze_ventilation_reason(temp, humi, wind)
        else:
            vent_grade, vent_reason = "-", "데이터 없음"
        # 환기 적합도 기준은 원하는 대로 수정 가능
        vent_recommend = vent_grade  # "매우 추천", "추천", "보통", "비추천"
        result.append({
            "date": key[:8],
            "time": key[8:10]+":00",
            "temperature": data.get("TMP", "?"),
            "humidity": data.get("REH", "?"),
            "windSpeed": data.get("WSD", "?"),
            "windDirectionDeg": data.get("VEC", "?"),  # 풍향(도)
            "windDirection": deg_to_wind_dir(vec),  #  풍향 문자
            "sky": {"1":"맑음","3":"구름많음","4":"흐림"}.get(data.get("SKY"), "?"),
            "precipitation": {"0":"없음","1":"비","2":"비/눈","3":"눈","4":"소나기"}.get(data.get("PTY"), "?"),
            "ventGrade": vent_grade,  # 등급화
            "ventReason": vent_reason,  # 사유
            "ventRecommend": vent_recommend,
        })
    return result, base_date, base_time

def get_latest_base_time(now):
    # 3시간 간격(02, 05, 08, 11, 14, 17, 20, 23)
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    h = now.hour
    m = now.minute
    for base in reversed(base_hours):
        if h > base or (h == base and m >= 10):  # 10분 이후부터 해당 발표
            return now.strftime("%Y%m%d"), f"{base:02d}00"
    # 2시 이전엔 전날 23시
    dt = now - timedelta(days=1)
    return dt.strftime("%Y%m%d"), "2300"

def deg_to_wind_dir(deg):
    # 입력값이 None 또는 문자열이면 처리
    try:
        deg = float(deg)
    except:
        return "?"
    dirs = ['북', '북북동', '북동', '동북동', '동', '동남동', '남동', '남남동',
            '남', '남남서', '남서', '서남서', '서', '서북서', '북서', '북북서']
    ix = int((deg + 11.25) // 22.5) % 16
    return dirs[ix]

def analyze_ventilation_reason(temp, humi, wind):
    temp, humi, wind = float(temp), float(humi), float(wind)
    reasons = []
    score = 0

    # 온도
    if 18 <= temp <= 25:
        reasons.append("온도 적합")
        score += 1
    elif 10 <= temp < 18 or 25 < temp <= 28:
        reasons.append("온도 약간 부적합")
    else:
        reasons.append("온도 부적합")

    # 습도
    if 40 <= humi <= 60:
        reasons.append("습도 적합")
        score += 1
    elif 30 <= humi < 40 or 60 < humi <= 70:
        reasons.append("습도 약간 부적합")
    else:
        reasons.append("습도 부적합")

    # 풍속
    if 0.5 <= wind < 3.1:
        reasons.append("풍속 적합")
        score += 1
    elif 0.3 <= wind < 0.5 or 3.1 <= wind < 5:
        reasons.append("풍속 약간 부적합")
    else:
        reasons.append("풍속 부적합")

    # 등급화
    if score == 3:
        grade = "매우 추천"
    elif score == 2:
        grade = "추천"
    elif score == 1:
        grade = "보통"
    else:
        grade = "비추천"
    return grade, ", ".join(reasons)


@app.route("/analyze_solar", methods=["POST"])
def analyze_solar():
    data = request.get_json()
    apt_code = data.get("apt_code")
    block = data.get("block")
    floor = int(data.get("floor"))
    direction = data.get("direction")
    dong_name = data.get("dong")

    # 좌표 정보
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

    fcst = get_ultra_forecast(lat, lon)
    nx, ny = latlon_to_xy(lat, lon)
    air_quality = get_air_quality(dong_name)

    # pm10_val과 pm25_val을 air_quality에서 직접 가져올 때 None 체크를 강화합니다.
    pm10_val = float(air_quality["pm10_val"]) if air_quality and "pm10_val" in air_quality and air_quality[
        "pm10_val"] is not None and air_quality["pm10_val"] != '-' else 0
    pm25_val = float(air_quality["pm25_val"]) if air_quality and "pm25_val" in air_quality and air_quality[
        "pm25_val"] is not None and air_quality["pm25_val"] != '-' else 0

    # 대기질 안내 메시지 생성 (HTML 테이블 형태로 변경)
    air_message = ""
    if air_quality:
        air_message += f"<h4 style='margin-bottom:5px;'>[대기질] {air_quality['station']}({air_quality['time']})</h4>"
        air_message += "<table class='air-quality-table'>"
        air_message += "<thead><tr>"
        air_message += f"<th rowspan='3'>{air_quality['station']}</th>"
        air_message += "<th></th>"
        air_message += "<th>환기 적합도</th>"
        air_message += "</tr></thead>"
        air_message += "<tbody>"

        air_message += f"<tr><td>미세먼지</td><td>미세먼지: {air_quality['PM10_text']}</td><td>{air_quality['ventilation_pm10']}</td></tr>"
        air_message += f"<tr><td>초미세먼지</td><td>초미세먼지: {air_quality['PM2.5_text']}</td><td>{air_quality['ventilation_pm25']}</td></tr>"
        air_message += f"<tr><td>오존</td><td>오존: {air_quality['O3_text']}</td><td>{air_quality['ventilation_o3']}</td></tr>"

        air_message += "</tbody></table>"
    else:
        air_message = "<span>[대기질 정보 없음] 인근 모든 측정소에 실시간 데이터가 없습니다.</span>"

    tz = pytz.timezone("Asia/Seoul")
    today = datetime.now().date()
    height = floor * 3
    now = tz.localize(datetime.now())
    results = []

    for h in range(5, 21):
        m = 0
        dt = tz.localize(datetime.combine(today, time(hour=h)))
        t_str = f"{h:02d}00"
        if dt <= now:
            minute = (dt.minute // 10) * 10
            base_time = dt.replace(minute=minute).strftime("%H%M")
            base_date = dt.strftime("%Y%m%d")
            weather = get_ultra_srt_ncst(KMA_API_KEY, nx, ny, base_date, base_time)
            source = "초단기실황"
        else:
            weather = fcst.get(t_str, {})
            source = "초단기예보"

        alt = get_altitude(lat, lon, dt)
        azi = get_azimuth(lat, lon, dt)
        raw_rad = get_radiation_direct(dt, alt) if alt > 0 else 0
        attenuated = raw_rad
        angle_factor = correction_factor(azi, apt_azimuth)
        final_rad = attenuated * angle_factor

        # (여기서 엣지 보정 계수 적용, 단 감쇠 없이 부드럽게)
        if 5 <= h < 7:
            # 층수에 따라 1~5% 정도만 증가
            edge_factor = 1 + (floor - 1) * 0.01 * (7 - h)
            final_rad *= edge_factor
        elif 18 < h <= 20:
            edge_factor = 1 + (floor - 1) * 0.01 * (h - 18)
            final_rad *= edge_factor

        # 아침엔 다음 시간, 저녁엔 이전 시간보다 커지지 않게
        if 5 <= h < 7:
            dt_next = tz.localize(datetime.combine(today, time(hour=h + 1)))
            alt_next = get_altitude(lat, lon, dt_next)
            azi_next = get_azimuth(lat, lon, dt_next)
            raw_rad_next = get_radiation_direct(dt_next, alt_next) if alt_next > 0 else 0
            attenuated_next = raw_rad_next
            angle_factor_next = correction_factor(azi_next, apt_azimuth)
            final_rad_next = attenuated_next * angle_factor_next
            if final_rad > final_rad_next:
                final_rad = final_rad_next

        elif 18 < h <= 20:
            dt_prev = tz.localize(datetime.combine(today, time(hour=h - 1)))
            alt_prev = get_altitude(lat, lon, dt_prev)
            azi_prev = get_azimuth(lat, lon, dt_prev)
            raw_rad_prev = get_radiation_direct(dt_prev, alt_prev) if alt_prev > 0 else 0
            attenuated_prev = raw_rad_prev
            angle_factor_prev = correction_factor(azi_prev, apt_azimuth)
            final_rad_prev = attenuated_prev * angle_factor_prev
            if final_rad > final_rad_prev:
                final_rad = final_rad_prev

        # 미세먼지 보정은 무조건 적용!
        if pm10_val is not None and pm10_val > 80:
            final_rad *= 0.9
        if pm10_val is not None and pm10_val > 100:
            final_rad *= 0.8
        if pm25_val is not None and pm25_val > 35:
            final_rad *= 0.9
        if pm25_val is not None and pm25_val > 50:
            final_rad *= 0.8

        # 날씨 데이터가 있을 때만 강수(비/눈) 0처리
        temp = weather.get("T1H") or weather.get("TMP") or "?"
        humi = weather.get("REH", "?")
        wind = weather.get("WSD", "?")
        pty = weather.get("PTY", "")
        sky = weather.get("SKY", "")
        if weather:
            if pty != "0" and pty != "":
                final_rad = 0

        results.append({
            "시간": f"{h}:{str(m).zfill(2)}",
            "타입": source,
            "기본 일사량": round(raw_rad, 2),
            "고도 보정": round(attenuated, 2),
            "최종 보정 일사량": round(final_rad, 2),
            "건조 적합도": get_dry_label(final_rad),
            "기온(℃)": temp,
            "습도(%)": humi,
            "풍속(m/s)": wind,
            "하늘": {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(sky, "?"),
            "강수": {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(pty, "?")
        })

    # 결과 문자열(프론트와 컬럼 일치)
    message = "시간\t타입\t기본 일사량\t고도 보정\t최종 보정 일사량\t건조 적합도\n"
    for r in results:
        message += f"{r['시간']}\t{r['타입']}\t{r['기본 일사량']}\t{r['고도 보정']}\t{r['최종 보정 일사량']}\t{r['건조 적합도']}\n"

    # 날씨 예보 표
    weather_message = f"[날씨 예보: {dong_name}]\n시간\t타입\t기온(℃)\t습도(%)\t풍속(m/s)\t하늘\t강수\n"
    for r in results:
        if r["기온(℃)"] != "?":
            weather_message += f"{r['시간']}\t{r['타입']}\t{r['기온(℃)']}\t{r['습도(%)']}\t{r['풍속(m/s)']}\t{r['하늘']}\t{r['강수']}\n"

    # 그래프(Chart.js와 동일)
    plt.figure(figsize=(13, 5))
    xs = [r["시간"] for r in results]
    plt.plot(xs, [r["기본 일사량"] for r in results], marker='o', label="기본 일사량")
    plt.plot(xs, [r["고도 보정"] for r in results], marker='^', label="고도 보정 일사량")
    plt.plot(xs, [r["최종 보정 일사량"] for r in results], marker='s', label="최종 보정 일사량")
    for x, y, label in zip(xs, [r["최종 보정 일사량"] for r in results], [r["건조 적합도"] for r in results]):
        plt.text(x, y + 10, label, ha='center', fontsize=9, color='blue')
    plt.xticks(rotation=45)
    plt.title(f"{block} {floor}층 {direction} - 5~20시(1시간 간격) 일사량/건조 적합도")
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

@app.route("/weekly")
def weekly():
    return render_template("weekly.html")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/weekly_weather")
def api_weekly_weather():
    dong_name = request.args.get("dong")
    print(f"[DEBUG] 받은 dong 파라미터: '{dong_name}'")
    conn = cx_Oracle.connect(**conn_info)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.LATITUDE, b.LONGITUDE
        FROM APARTMENTS_BLOCK b
        JOIN APARTMENTS_ADDRESS a ON b.KAPT_CODE = a.KAPT_CODE
        WHERE a.DONG = :1
        FETCH FIRST 1 ROWS ONLY
    """, (dong_name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify([])
    lat, lon = float(row[0]), float(row[1])

    # 1) 단기예보 결과(시간별)
    result, base_date, base_time = get_vilage_fcst_all(lat, lon)

    # 2) 미세먼지 예보 결과(일별)
    df_dust = get_latest_daejeon_forecasts()

    # 3) 날짜별 미세먼지 예보 등급 dict로 변환
    # 예시: dust_grade["2024-07-02"]["미세먼지(PM10)"] = '보통'
    dust_grade = {}
    for _, row in df_dust.iterrows():
        day = row["예보일"]
        kind = row["예보종류"]
        grade = row["예보등급"]
        if day not in dust_grade:
            dust_grade[day] = {}
        dust_grade[day][kind] = grade

    # 4) 결과에 dust 예보 등급 및 환기추천 보정 적용
    # result 리스트의 각 아이템: 날짜/시간/환기추천... 포함
    for item in result:
        day_str = f"{item['date'][:4]}-{item['date'][4:6]}-{item['date'][6:]}"
        pm10_grade = dust_grade.get(day_str, {}).get("미세먼지(PM10)", "-")
        pm25_grade = dust_grade.get(day_str, {}).get("초미세먼지(PM2.5)", "-")
        o3_grade = dust_grade.get(day_str, {}).get("오존(O3)", "-")

        # 미세먼지 예보가 없으면 dust_recommend=True (즉, 미세먼지는 무시)
        if pm10_grade is None or pm25_grade is None or o3_grade is None or pm10_grade == '-' or pm25_grade == '-' or o3_grade == '-':
            item["dustRecommend"] = True
            item["dustGrade"] = "예보 없음"
            item["ventReason"] += " (미세먼지 예보 없음, 미세먼지 조건 미적용)"
        elif not (is_dust_good(pm10_grade) and is_dust_good(pm25_grade) and is_dust_good(o3_grade)):
            item["dustRecommend"] = False
            item["dustGrade"] = f"PM10:{pm10_grade}, PM2.5:{pm25_grade}, O3:{o3_grade} "
            item["ventRecommend"] = "비추천"
            item["ventReason"] += " (미세먼지 예보 부적합)"
        else:
            item["dustRecommend"] = True
            item["dustGrade"] = f"PM10:{pm10_grade}, PM2.5:{pm25_grade}, O3:{o3_grade}"

    # 5) 환기 추천만 필터링(미세먼지까지 반영)
    recommend_times = [item for item in result if item["ventRecommend"] and item["dustRecommend"]]

    return jsonify({
        "baseDate": base_date,
        "baseTime": base_time,
        "weatherAll": result,          # 전체 예보(모든 시간대)
        "recommendTimes": recommend_times,  # 환기 추천만 추린 시간대(배열)
        "dustForecast": df_dust.to_dict(orient="records")  # 원본 dust 예보도 프론트에 전달
    })

if __name__ == "__main__":
    app.run(debug=True)