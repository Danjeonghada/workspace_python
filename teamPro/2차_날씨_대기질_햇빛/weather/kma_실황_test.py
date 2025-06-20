import pandas as pd
import requests
from datetime import datetime, timedelta

EXCEL_WEATHER = "좌표목록.csv"
KMA_AUTH_KEY = "DIdS2JmzSt6HUtiZs2re8g"
PTY_CODE = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}

def get_gis_xy_from_dong(dong_name):
    df = pd.read_csv(EXCEL_WEATHER)
    df = df[df['3단계'].notna()]
    row = df[df['3단계'] == dong_name]
    if row.empty:
        raise Exception(f"'{dong_name}'의 좌표 정보를 찾을 수 없습니다.")
    return int(row.iloc[0]['격자 X']), int(row.iloc[0]['격자 Y'])

def get_ultra_srt_ncst(api_key, nx, ny, base_date, base_time):
    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey={api_key}"
    )
    res = requests.get(url)
    data = res.json()
    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    weather = {item['category']: item['obsrValue'] for item in items}
    return weather

def print_ultra_srt_ncst_today(dong_name, api_key):
    nx, ny = get_gis_xy_from_dong(dong_name)
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    # 05:00 ~ 17:00 10분 단위
    start = now.replace(hour=5, minute=0, second=0, microsecond=0)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)
    times = []
    t = start
    while t <= end:
        times.append(t)
        t += timedelta(minutes=10)

    print(f"==== {dong_name} ({nx},{ny}) {base_date} 초단기실황(관측) ====")
    for dt in times:
        base_time = dt.strftime("%H%M")
        try:
            weather = get_ultra_srt_ncst(api_key, nx, ny, base_date, base_time)
            if not weather:
                print(f"[{base_time}] 데이터 없음")
                continue
            print(
                f"[{base_time}] "
                f"기온:{weather.get('T1H','-')}°C "
                f"습도:{weather.get('REH','-')}% "
                f"풍속:{weather.get('WSD','-')}m/s "
                f"하늘:{weather.get('SKY','-')} "
                f"강수:{PTY_CODE.get(weather.get('PTY','0'),'알수없음')} "
                f"1시간강수:{weather.get('RN1','-')}"
            )
        except Exception as e:
            print(f"[{base_time}] 에러: {e}")

if __name__ == "__main__":
    dong_name = "둔산동"
    KMA_AUTH_KEY = "DIdS2JmzSt6HUtiZs2re8g"
    print_ultra_srt_ncst_today(dong_name, KMA_AUTH_KEY)