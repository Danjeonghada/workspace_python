import pandas as pd
import requests
from datetime import datetime, timedelta

EXCEL_FILE = "좌표목록.csv"

PTY_CODE = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기"
}

SKY_CODE = {
    "1": "맑음",
    "3": "구름 많음",
    "4": "흐림"
}

def get_base_date_time():
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")

    # 기준 시각은 30분 단위 (예보는 매 30분 갱신됨)
    if now.minute < 45:
        base_time = (now - timedelta(hours=1)).strftime("%H30")
    else:
        base_time = now.strftime("%H30")
    return base_date, base_time

def get_coords_from_file(dong_name):
    df = pd.read_csv(EXCEL_FILE)
    row = df[df['3단계'] == dong_name]
    if row.empty:
        print(f"[오류] '{dong_name}'의 좌표 정보를 찾을 수 없습니다.")
        return None
    return int(row.iloc[0]['격자 X']), int(row.iloc[0]['격자 Y'])

def get_forecast_weather(nx, ny, base_date, base_time):
    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtFcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey=DIdS2JmzSt6HUtiZs2re8g"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    items = data["response"]["body"]["items"]["item"]

    # 예보 항목 정리: fcstTime → { category: value }
    forecast_by_time = {}
    for item in items:
        time = item['fcstTime']
        category = item['category']
        value = item['fcstValue']
        if time not in forecast_by_time:
            forecast_by_time[time] = {}
        forecast_by_time[time][category] = value
    return forecast_by_time

def display_all_forecast(forecast_by_time, dong_name):
    print(f"\n📅 [{dong_name}] 초단기예보 - 향후 6시간:")
    for time in sorted(forecast_by_time.keys()):
        data = forecast_by_time[time]
        print(f"\n🕒 {time[:2]}시 {time[2:]}분 예보:")
        print(f"🌡️ 기온: {data.get('T1H', '?')}℃")
        print(f"💧 습도: {data.get('REH', '?')}%")
        print(f"💨 풍속: {data.get('WSD', '?')} m/s, 풍향: {data.get('VEC', '?')}°")
        print(f"☁️ 하늘 상태: {SKY_CODE.get(data.get('SKY', '?'), '알 수 없음')}")
        print(f"🌧️ 강수 형태: {PTY_CODE.get(data.get('PTY', '0'), '알 수 없음')}, 강수량: {data.get('RN1', '0')} mm")

def get_weather_forecast_full(dong_name):
    coords = get_coords_from_file(dong_name)
    if coords is None:
        return
    nx, ny = coords
    base_date, base_time = get_base_date_time()

    try:
        forecast = get_forecast_weather(nx, ny, base_date, base_time)
        display_all_forecast(forecast, dong_name)
    except Exception as e:
        print("[예보 API 오류 발생]", e)

if __name__ == "__main__":
    dong_input = input("예보를 조회할 동 이름을 입력하세요 (예: 둔산동): ")
    get_weather_forecast_full(dong_input)
