import requests
import json

url = "http://localhost:5000/predict"  # 전기요금 예측 API 주소
headers = {"Content-Type": "application/json"}

data = {
    "dong": "둔산동",  # 예측할 동 이름
    "year": 2025       # 예측할 연도
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print("✅ 예측 결과:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print("❌ 오류:", response.status_code)
    print(response.text)