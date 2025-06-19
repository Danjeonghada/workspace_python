from flask import Flask, request, jsonify
import pandas as pd
import requests
from datetime import datetime, timedelta
from pyproj import Transformer

app = Flask(__name__)

# ✅ 공통 설정
EXCEL_WEATHER = "좌표목록.csv"
EXCEL_AIR = "tm_coords_from_api.csv"
KMA_AUTH_KEY = "DIdS2JmzSt6HUtiZs2re8g"
AIR_SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

PTY_CODE = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
transformer = Transformer.from_crs("epsg:4326", "epsg:2097", always_xy=True)


# ✅ 날씨 예보 API (초단기예보 6시간)
def get_weather(dong_name):
    try:
        df = pd.read_csv(EXCEL_WEATHER)
        row = df[df['3단계'] == dong_name]
        if row.empty:
            return {"error": f"'{dong_name}'의 좌표 정보를 찾을 수 없습니다."}

        nx, ny = int(row.iloc[0]['격자 X']), int(row.iloc[0]['격자 Y'])

        # 기준 시간 계산 (30분 단위 기준)
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        if now.minute < 45:
            base_time = (now - timedelta(hours=1)).strftime("%H30")
        else:
            base_time = now.strftime("%H30")

        # API 요청
        url = (
            "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
            f"?pageNo=1&numOfRows=1000&dataType=JSON"
            f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
            f"&authKey={KMA_AUTH_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        items = data["response"]["body"]["items"]["item"]

        # 예보 항목 구성
        forecast_by_time = {}
        for item in items:
            time = item['fcstTime']
            cat = item['category']
            val = item['fcstValue']
            if time not in forecast_by_time:
                forecast_by_time[time] = {}
            forecast_by_time[time][cat] = val

        # 최대 6시간 예보 추출
        PTY_CODE = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
        SKY_CODE = {"1": "맑음", "3": "구름 많음", "4": "흐림"}

        result = []
        for time in sorted(forecast_by_time.keys())[:6]:  # 최대 6시간
            data = forecast_by_time[time]
            result.append({
                "time": f"{time[:2]}:{time[2:]}",
                "temp_C": data.get("T1H", "?"),
                "humidity_%": data.get("REH", "?"),
                "rain_type": PTY_CODE.get(data.get("PTY", "0"), "알 수 없음"),
                "rain_mm": data.get("RN1", "0"),
                "sky": SKY_CODE.get(data.get("SKY", "?"), "알 수 없음"),
                "wind_speed_mps": data.get("WSD", "?"),
                "wind_direction_deg": data.get("VEC", "?")
            })

        return {
            "dong": dong_name,
            "base_date": base_date,
            "base_time": base_time,
            "forecast": result
        }

    except Exception as e:
        return {"error": str(e)}



# ✅ 대기질 API
def get_air_quality(dong_name):
    try:
        df = pd.read_csv(EXCEL_AIR)
        row = df[df["3단계"] == dong_name]
        if row.empty:
            return {"error": f"'{dong_name}'의 TM 좌표를 찾을 수 없습니다."}

        tm_x, tm_y = row.iloc[0]["TM_X"], row.iloc[0]["TM_Y"]

        # 측정소 찾기
        station_res = requests.get(
            "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList",
            params={
                "tmX": tm_x,
                "tmY": tm_y,
                "returnType": "json",
                "serviceKey": AIR_SERVICE_KEY,
                "ver": "1.1"
            }
        )
        station_data = station_res.json()
        station_list = station_data.get("response", {}).get("body", {}).get("items", [])
        if not station_list:
            return {"error": "측정소를 찾을 수 없습니다."}
        station = station_list[0]["stationName"]

        # 대기질 정보
        air_res = requests.get(
            "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty",
            params={
                "stationName": station,
                "returnType": "json",
                "serviceKey": AIR_SERVICE_KEY,
                "dataTerm": "DAILY",
                "ver": "1.3"
            }
        )
        air_data = air_res.json()
        items = air_data.get("response", {}).get("body", {}).get("items", [])
        if not items:
            return {"error": "대기질 데이터를 찾을 수 없습니다."}

        item = items[0]
        def grade_text(code):
            return {"1": "좋음", "2": "보통", "3": "나쁨", "4": "매우나쁨"}.get(str(code), "-")

        return {
            "dong": dong_name,
            "station": station,
            "time": item.get("dataTime"),
            "PM10": f"{item.get('pm10Value')} ㎍/㎥ ({grade_text(item.get('pm10Grade'))})",
            "PM2.5": f"{item.get('pm25Value')} ㎍/㎥ ({grade_text(item.get('pm25Grade'))})",
            "O3": f"{item.get('o3Value')} ppm ({grade_text(item.get('o3Grade'))})"
        }

    except Exception as e:
        return {"error": str(e)}


# ✅ Flask 라우팅
@app.route("/weather")
def weather_api():
    dong = request.args.get("dong", "").strip()
    return jsonify(get_weather(dong))


@app.route("/air_quality")
def air_quality_api():
    dong = request.args.get("dong", "").strip()
    return jsonify(get_air_quality(dong))

@app.route("/status")
def status_api():
    dong = request.args.get("dong", "").strip()
    weather = get_weather(dong)
    air = get_air_quality(dong)
    return jsonify({
        "dong": dong,
        "weather": weather,
        "air_quality": air
    })


# ✅ 실행
if __name__ == "__main__":
    app.run(debug=True)
