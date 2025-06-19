import requests
from datetime import datetime, timedelta

# 동 → 기상청 격자 좌표 매핑
DONG_TO_XY = {
    "용문동": (67, 100),
    "둔산동": (67, 99),
    "탄방동": (68, 99),
    "가장동": (66, 99),
    "월평동": (66, 98),
}

# 강수형태 코드
PTY_CODE = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기"
}

# 기준 시간 계산 함수 (현재 시간 기준으로 한 시간 전)
def get_base_date_time():
    now = datetime.now() - timedelta(hours=1)
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")
    return base_date, base_time

# 날씨 조회 함수
def get_weather_by_dong(dong_name: str):
    if dong_name not in DONG_TO_XY:
        print(f"[오류] '{dong_name}'은(는) 등록된 지역이 아닙니다.")
        return

    nx, ny = DONG_TO_XY[dong_name]
    base_date, base_time = get_base_date_time()

    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        f"&authKey=DIdS2JmzSt6HUtiZs2re8g"  # 테스트 키 (실제 서비스 시 개인 키 발급 필요)
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 정상 데이터 여부 확인
        if "response" not in data or "body" not in data["response"]:
            print("[에러] 응답 데이터 구조가 예상과 다릅니다.")
            print("응답 원문:", data)
            return

        items = data["response"]["body"]["items"]["item"]
        weather = {item['category']: item['obsrValue'] for item in items}

        # 값 추출
        temp = weather.get("T1H", "?")  # 기온
        humidity = weather.get("REH", "?")  # 습도
        pty = PTY_CODE.get(weather.get("PTY", "0"), "알 수 없음")
        wind_speed = weather.get("WSD", "?")
        wind_dir = weather.get("VEC", "?")

        # 결과 출력
        print(f"[{dong_name}] 기준시각: {base_date} {base_time}")
        print(f"기온: {temp}℃, 습도: {humidity}%, 강수형태: {pty}")
        print(f"풍속: {wind_speed} m/s, 풍향: {wind_dir}°")

    except requests.RequestException as e:
        print(f"[요청 실패] 네트워크 오류: {e}")
    except KeyError as e:
        print(f"[에러] 응답 파싱 실패 - 누락된 키: {e}")
    except Exception as e:
        print(f"[예외] 처리 중 오류 발생: {e}")

# 테스트 실행
if __name__ == "__main__":
    get_weather_by_dong("둔산동")
