#기상청_지상(종관,ASOS)일자료 조회서비스
#https://www.data.go.kr/data/15059093/openapi.do#tab_layer_detail_function
#https://www.data.go.kr/iim/api/selectAPIAcountView.do
import pandas as pd
import requests
import datetime
import math
import matplotlib.pyplot as plt
import urllib3 # 추가: SSL 경고를 비활성화하기 위함

# --- SSL 인증 경고 무시 (테스트 목적, 보안상 권장되지 않음) ---
# 이 부분을 추가하여 SSL 오류를 임시로 회피합니다.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# -------------------------------------------------------------

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 음수 부호 깨짐 방지

# 위도 경도 대전으로 바꿔야함 (아직 안 바꿈)
latitude = 37.5665
longitude = 126.9780


service_key = 'LFriN6wdYvRJGUwZsh3ZL2lfyNtLaixTqOTAfeV8QPbhcRD8tJw5CkKQTiwdc2NS3Oc6uJF5bwadoHx42FHmAA=='

# 조회 날짜 설정
today = datetime.date.today()
date = today - datetime.timedelta(days=1) # 어제 날짜 (예: 2025년 6월 3일)
date_str = date.strftime('%Y%m%d')
print(f"조회 날짜: {date_str}") # 조회 날짜 출력aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaadd


station_id = '133' # 대전코드
print(f"조회 지점: {station_id} (대전)")

# 요청 URL
url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'
params = {
    'serviceKey': service_key,
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'JSON',
    'dataCd': 'ASOS',
    'dateCd': 'DAY',
    'startDt': date_str,
    'endDt': date_str,
    'stnIds': station_id
}

# 📡 API 요청 및 응답 처리
try:
    print(f"API 요청 URL: {requests.Request('GET', url, params=params).prepare().url}")

    # verify=False 옵션을 추가하여 SSL 인증서 검증을 건너뜁니다.
    response = requests.get(url, params=params, verify=False, timeout=10) # timeout 추가
    response.raise_for_status() # HTTP 오류 (4xx, 5xx)가 발생하면 예외를 발생시킴

    items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    if items:
        # ☀️ 일사량 데이터 추출 (단위: MJ/m²)
        sum_gsr = float(items[0].get('sumGsr', 0))
        # ASOS 데이터는 MJ/m^2 이고, 이를 W/m^2 로 변환 (하루 평균)
        # 1 MJ/m^2 = 1,000,000 J/m^2
        # 1 day = 24 * 3600 seconds = 86400 seconds
        # 평균 W/m^2 = (J/m^2) / s
        # 따라서, I0 (W/m^2) = sum_gsr (MJ/m^2) * 1,000,000 / 86400
        # 이 변환 계수 11.574는 sumGsr을 '하루 동안의 평균 일사량'으로 볼 때 사용됩니다.
        # 기존 코드의 11.574 계수를 유지합니다.
        I0 = sum_gsr * 11.574
        print(f"[✅ API 호출 성공] {date_str} {station_id}의 일사량 (sumGsr): {sum_gsr} MJ/m²")
        print(f"변환된 지표면 기준 일사량 (I0): {I0:.2f} W/m²")
    else:
        print(f"⚠️ API 응답에 날짜({date_str}) 또는 지점({station_id})에 대한 데이터가 없습니다.")
        print(f"  → API 응답 메시지: {response.json().get('response', {}).get('header', {}).get('resultMsg', '메시지 없음')}")
        I0 = None
except requests.exceptions.SSLError as e:
    print(f"[❌ SSL 오류 발생]: {e}")
    print("  → SSL 인증서 또는 TLS 버전 관련 문제일 수 있습니다.")
    print("  → 'verify=False' 옵션을 사용하여 일시적으로 검증을 비활성화했지만, 문제가 지속됩니다.")
    print("  → 파이썬 환경의 SSL 인증서 문제 해결이 필요합니다 (Anaconda/pip 업데이트, 인증서 설치 스크립트 실행 등).")
    I0 = None
except requests.exceptions.RequestException as e:
    print(f"⚠️ API 요청 중 오류 발생: {e}")
    I0 = None
except Exception as e:
    print(f"⚠️ 예상치 못한 오류 발생: {e}")
    I0 = None


if I0 is None:
    print("API 데이터 로드에 실패했거나 유효한 일사량 데이터를 얻지 못하여 프로그램이 종료됩니다.")
    exit()



excel_file_path = "한국부동산원_공동주택 단지 식별정보_동정보_20240809.xlsx"
try:
    df = pd.read_excel(excel_file_path)
    print(f"[✅ 엑셀 파일 로드 성공]: {excel_file_path}")
except FileNotFoundError:
    print(f"[❌ 파일 오류]: '{excel_file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
    exit()
except Exception as e:
    print(f"[❌ 엑셀 파일 로드 중 오류 발생]: {e}")
    exit()

# '지상층수' 컬럼이 숫자인지 확인하고 숫자가 아니면 NaN으로 처리함
df['지상층수'] = pd.to_numeric(df['지상층수'], errors='coerce')

# 고도 계산: 층수 × 3미터
df['상대고도(m)'] = df['지상층수'] * 3

#  일사량 보정 함수 정의
def adjust_radiation(base_radiation_value, floor, floor_height=3.0, k=0.00013):
    """
    base_radiation_value : 지표면 기준 일사량 (W/m²)
    floor : 층수
    floor_height : 층당 높이 (m)
    k : 감쇠 계수 (대기 중 일사량 감소율)
    """
    if pd.isna(floor) or base_radiation_value is None or base_radiation_value <= 0:
        return None # 유효하지 않은 층수나 기준 일사량이 없으면 None 반환

    height = floor * floor_height
    I = base_radiation_value * math.exp(-k * height)
    return round(I, 2)

# 📊 보정된 일사량 계산 및 추가
# I0 값을 adjust_radiation 함수에 직접 전달
df['보정_직달일사량(W/m²)'] = df['지상층수'].apply(lambda x: adjust_radiation(I0, x))

print("\n--- 계산 결과 (유효한 데이터 상위 10개) ---")
print(df[['지상층수', '상대고도(m)', '보정_직달일사량(W/m²)']].dropna(subset=['보정_직달일사량(W/m²)']).head(10))


df_plot = df.dropna(subset=['보정_직달일사량(W/m²)'])
df_plot = df_plot[df_plot['지상층수'] <= 100] # 지상층수가 100층 이하인 데이터만 선택이긴한데 필요없을듯

if not df_plot.empty:
    plt.figure(figsize=(10, 5))
    plt.scatter(df_plot['지상층수'], df_plot['보정_직달일사량(W/m²)'], color='orange', alpha=0.7)
    plt.title("지상층수에 따른 보정된 직달일사량 (대전, " + date_str + " 데이터 기반, 100층 이하)")
    plt.xlabel("지상층수")
    plt.ylabel("보정된 직달일사량 (W/m²)")
    plt.grid(True)
    plt.show()
else:
    print("\n❗ 그래프를 그릴 유효한 데이터가 없습니다. '지상층수' 또는 '보정_직달일사량' 컬럼에 유효한 데이터가 있는지 확인해주세요.")
try:
    df.to_excel("층수별_보정_직달일사량.xlsx", index=False)
    print("\n[✅ 결과 저장 완료]: '층수별_보정_직달일사량.xlsx' 파일이 생성되었습니다.")
except Exception as e:
    print(f"[❌ 파일 저장 오류]: 엑셀 파일 저장 중 오류 발생 - {e}")

#현재 1층을 3m로 잡고 층수에 따라 직달일사량을 잡음
#이제 아파트마다 방향이 다르니까 아파트방향_주소_아파트명_최종_정제csv를 넣어서 계산해야함