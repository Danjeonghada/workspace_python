import requests

# 📌 위경도 좌표
lat = 36.342582
lon = 127.392990

# 📌 VWorld API 키 입력 (반드시 본인 키로 교체!)
api_key = 'F988F1E5-42AE-3BC2-9367-493BB6BA3661'


url = f"https://api.vworld.kr/req/data?service=data&request=getfeature&format=json&key={api_key}&data=dem&geomFilter=point({lon} {lat})"

response = requests.get(url)

try:
    data = response.json()
    print("📦 전체 응답 확인:")
    print(data)  # 구조 확인용

    # 고도 추출
    elevation = data['response']['result']['featureCollection']['features'][0]['properties']['elevation']
    print(f"✅ 위도: {lat}, 경도: {lon} → 고도: {elevation} m")
except Exception as e:
    print("⚠️ 고도 정보를 불러오지 못했습니다.")
    print("🔍 에러:", str(e))
    print("📜 응답 내용:", response.text)