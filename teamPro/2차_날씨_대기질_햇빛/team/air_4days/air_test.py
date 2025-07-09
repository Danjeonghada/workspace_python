from flask import Flask, render_template
import requests
import pandas as pd

app = Flask(__name__)

AIR_SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

def get_latest_daejeon_forecasts():
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMinuDustFrcstDspth"
    params = {
        'serviceKey': AIR_SERVICE_KEY,
        'returnType': 'json',
        'searchDate': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'ver': '1.1'
    }
    res = requests.get(url, params=params, timeout=8)
    data = res.json()
    items = (
        data.get('response', {})
            .get('body', {})
            .get('items', [])
    )
    code_map = {'PM10': '미세먼지(PM10)', 'PM25': '초미세먼지(PM2.5)', 'O3': '오존(O3)'}
    result = []
    for item in items:
        code = item.get('informCode')
        if code not in code_map:
            continue
        date = item.get('informData')  # 예보일
        # 대전 등급 추출
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
    # ▶ 날짜/종류별로 "발표시각" 최신 1개만 남김
    df = pd.DataFrame(result)
    df = df.sort_values(by=["예보일", "예보종류", "발표시각"], ascending=[True, True, False])
    df = df.drop_duplicates(subset=["예보일", "예보종류"], keep="first").reset_index(drop=True)
    return df

@app.route('/')
def index():
    df = get_latest_daejeon_forecasts()
    table_html = df.to_html(classes='forecast-table', index=False, border=0, justify='center')
    return render_template('index.html', table_html=table_html)

if __name__ == '__main__':
    app.run(debug=True)
