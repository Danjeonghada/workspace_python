import requests
import pandas as pd

AIR_SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

def get_daejeon_forecasts():
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth"
    params = {
        'serviceKey': AIR_SERVICE_KEY,
        'returnType': 'json',
        'searchDate': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'ver': '1.1'
    }
    res = requests.get(url, params=params, timeout=6)
    data = res.json()
    items = (
        data.get('response', {})
            .get('body', {})
            .get('items', [])
    )
    result = []
    for item in items:
        code_map = {'PM10': '미세먼지(PM10)', 'PM25': '초미세먼지(PM2.5)', 'O3': '오존(O3)'}
        code = item.get('informCode')
        if code not in code_map:
            continue
        date = item.get('informData')  # 예보일
        # 지역별 등급 파싱
        grade = '-'
        grade_text = item.get('informGrade', '')
        for region_part in grade_text.split(','):
            region_part = region_part.strip()
            if region_part.startswith("대전"):
                parts = region_part.split(":")
                if len(parts) > 1:
                    grade = parts[1].strip()
        desc = item.get('informCause', '')  # 예보설명
        announce_time = item.get('dataTime', '')  # 발표시각
        result.append({
            "예보종류": code_map[code],
            "예보일": date,
            "예보등급": grade,
            "발표시각": announce_time,
            "예보설명": desc
        })
    # 날짜 & 예보종류 기준 정렬
    df = pd.DataFrame(result)
    df = df.sort_values(by=["예보일", "예보종류"]).reset_index(drop=True)
    return df

# 표 출력
df = get_daejeon_forecasts()
print(df)

# HTML 표로 변환하고 싶다면 아래처럼 사용
# html_table = df.to_html(index=False)
# print(html_table)
