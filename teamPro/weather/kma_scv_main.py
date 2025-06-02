import pandas as pd
import requests
from datetime import datetime, timedelta

# ✅ 파일 경로
EXCEL_FILE = "좌표목록.csv"

# ✅ 강수 코드
PTY_CODE = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기"
}

# ✅ 기준 시간 계산
def get_base_date_time():
    now = datetime.now() - timedelta(hours=1)
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")
    return base_date, base_time

# ✅ 동 이름 → 격자 좌표 추출
def get_coords_from_file(dong_name):
    if EXCEL_FILE.endswith(".csv"):
        df = pd.read_csv(EXCEL_FILE)
    else:
        df = pd.read_excel(EXCEL_FILE)

    df = df[df['3단계'].notna()]  # NaN 제거

    row = df[df['3단계'] == dong_name]
    if row.empty:
        print(f"[오류] '{dong_name}'의 좌표 정보를 찾을 수 없습니다.")
        return None
    return int(row.iloc[0]['격자 X']), int(row.iloc[0]['격자 Y'])

# ✅ 날씨 API 호출
def get_weather_by_dong(dong_name):
    coords = get_coords_from_file(dong_name)
    if coords is None:
        return

    nx, ny = coords
    base_date, base_time = get_base_date_time()

    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey=DIdS2JmzSt6HUtiZs2re8g"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = data["response"]["body"]["items"]["item"]
        weather = {item['category']: item['obsrValue'] for item in items}

        temp = weather.get("T1H", "?")
        humidity = weather.get("REH", "?")
        pty = PTY_CODE.get(weather.get("PTY", "0"), "알 수 없음")
        wind_speed = weather.get("WSD", "?")
        wind_dir = weather.get("VEC", "?")

        print(f"\n[{dong_name}] 기준시각: {base_date} {base_time}")
        print(f"기온: {temp}℃, 습도: {humidity}%, 강수형태: {pty}")
        print(f"풍속: {wind_speed} m/s, 풍향: {wind_dir}°")

    except Exception as e:
        print("[API 오류 발생]", e)

# ✅ 사용자 입력
if __name__ == "__main__":
    dong_input = input("날씨를 조회할 동 이름을 입력하세요 (예: 둔산동, 가양동 등): ")
    get_weather_by_dong(dong_input)
