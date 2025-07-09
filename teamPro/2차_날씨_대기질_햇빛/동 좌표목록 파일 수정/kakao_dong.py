import pandas as pd
import requests
import time

# 0. 카카오 REST API 키 입력 (내 애플리케이션 > 앱키 > REST API 키)
KAKAO_REST_API_KEY = '21a282db2780ca99a78bc590751dddce'

# 1. 미존재_동목록.csv 파일에서 동 이름 읽기
df = pd.read_csv('미존재_동목록.csv')
dong_list = df['미존재_동목록'].dropna().tolist()

# 2. 카카오 API로 위경도 조회 함수
def get_latlng_kakao(dong_name):
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    params = {"query": f"대전광역시 {dong_name}"}  # '대전광역시'는 실제 지역에 맞게 수정!
    resp = requests.get(url, headers=headers, params=params).json()
    if resp.get('documents'):
        lat = resp['documents'][0]['y']
        lng = resp['documents'][0]['x']
        return float(lat), float(lng)
    else:
        return None, None

# 3. 동별 위경도 찾기 & 결과 저장
results = []
for dong in dong_list:
    lat, lng = get_latlng_kakao(dong)
    results.append({"동이름": dong, "위도": lat, "경도": lng})
    print(f"{dong}: lat={lat}, lng={lng}")
    time.sleep(0.2)  # API 과호출 방지 (0.2초 딜레이)

# 4. 결과를 CSV로 저장
result_df = pd.DataFrame(results)
result_df.to_csv('미존재_동목록_좌표.csv', index=False, encoding='utf-8-sig')
print("좌표 저장 완료!")