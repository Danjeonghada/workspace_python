import pandas as pd
import requests
from datetime import datetime

# 설정
EXCEL_WEATHER = "좌표목록.csv"
KMA_AUTH_KEY = "여기에_네_API_KEY_입력"  # apihub.kma.go.kr에서 발급받은 단기예보 key
PTY_CODE = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
SKY_CODE = {"1": "맑음", "3": "구름많음", "4": "흐림"}

def get_gis_xy_from_dong(dong_name):
    df = pd.read_csv(EXCEL_WEATHER)
    df = df[df['3단계'].notna()]
    row = df[df['3단계'] == dong_name]
    if row.empty:
        raise Exception(f"'{dong_name}'의 좌표 정보를 찾을 수 없습니다.")
    return int(row.iloc[0]['격자 X']), int(row.iloc[0]['격자 Y'])

def get_vilage_fcst(api_key, nx, ny, base_date, base_time):
    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey={api_key}"
    )
    res = requests.get(url)
    data = res.json()
    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    fcst = {}
    for item in items:
        t = item['fcstTime']   # 예보 시간
        cat = item['category']
        val = item['fcstValue']
        if t not in fcst:
            fcst[t] = {}
        fcst[t][cat] = val
    return fcst

def print_vilage_fcst_today(dong_name, api_key):
    nx, ny = get_gis_xy_from_dong(dong_name)
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    # 단기예보 발표시각 결정(오늘 5시, 17시 중 가장 최근)
    hour = now.hour
    base_time = "0500" if hour < 15 else "1700"
    fcst = get_vilage_fcst(api_key, nx, ny, base_date, base_time)

    print(f"==== {dong_name} ({nx},{ny}) {base_date} 단기예보 ====")
    for h in range(4, 21):  # 4~20시까지 출력(기상청 표준 시간)
        t_str = f"{h:02d}00"
        f = fcst.get(t_str, {})
        if not f:
            print(f"[{t_str}] 예보 없음")
            continue
        print(
            f"[{t_str}] "
            f"기온:{f.get('TMP','-')}°C "
            f"습도:{f.get('REH','-')}% "
            f"풍속:{f.get('WSD','-')}m/s "
            f"하늘:{SKY_CODE.get(f.get('SKY',''),'-')} "
            f"강수:{PTY_CODE.get(f.get('PTY','0'),'알수없음')} "
            f"강수량:{f.get('PCP','-')}"
        )

if __name__ == "__main__":
    dong_name = "둔산동"   # 원하는 동 이름
    KMA_AUTH_KEY = "DIdS2JmzSt6HUtiZs2re8g"   # 반드시 본인 단기예보 key로!
    print_vilage_fcst_today(dong_name, KMA_AUTH_KEY)
