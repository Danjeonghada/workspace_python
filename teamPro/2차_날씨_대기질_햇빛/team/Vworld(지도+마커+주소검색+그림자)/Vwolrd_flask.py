# flask.py
import pandas as pd
from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)


CSV_FILE = "아파트방향_주소_아파트명_최종_정제.csv"

# Flask 앱 시작 시 CSV 파일 로드
try:
    # CSV 파일을 UTF-8 인코딩
    df_addresses = pd.read_csv(CSV_FILE, encoding='utf-8', on_bad_lines='skip')

    df_addresses.columns = df_addresses.columns.str.replace(r"\(.*\)", "", regex=True).str.strip()
     #컬럼확인한거
    required_columns = ['아파트명', '위도', '경도', '방향', '주소']
    if not all(col in df_addresses.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df_addresses.columns]
        raise ValueError(f"CSV 파일에 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")

    print(f"'{CSV_FILE}' 파일 로드 성공!")

except FileNotFoundError:
    print(f"[오류] '{CSV_FILE}' 파일이 없습니다. 이 파일을 '{CSV_FILE}'와 같은 폴더에 넣어주세요.")
    df_addresses = pd.DataFrame()
except Exception as e:
    print(f"[오류] CSV 파일 로드 중 문제가 발생했습니다: {e}")
    df_addresses = pd.DataFrame()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_address', methods=['POST'])
def search_address():
    # 사용자가 입력한 주소를 JSON 형태로 받아옵니다.
    data = request.get_json()
    search_query = data.get('address')
    print(f"검색 요청 주소: {search_query}")
    if df_addresses.empty:
        print("데이터 로드 실패로 검색을 수행할 수 없습니다.")
        return jsonify({'success': False, 'message': '서버 데이터 준비 중 오류 발생. 관리자에게 문의하세요.'})
    matched_address_df = df_addresses[df_addresses['아파트명'].str.contains(search_query, na=False, case=False)]

    if not matched_address_df.empty:
        apartment_info = matched_address_df.iloc[0]
        apartment_name = apartment_info['아파트명']
        latitude = float(apartment_info['위도']) # 숫자로 변환
        longitude = float(apartment_info['경도']) # 숫자로 변환
        direction = apartment_info['방향']
        address = apartment_info['주소']

        # 주소에서 동 이름 추출
        match = re.search(r"(\S+동)", address)
        if match:
            dong_name = match.group(1)
        else:
            dong_name = "정보 없음" # 동 정보를 찾지 못할 경우 기본값 설정

        print(f"CSV에서 찾은 아파트명: {apartment_name}")
        print(f"찾은 좌표: 위도 {latitude}, 경도 {longitude}")
        print(f"아파트 방향: {direction}, 동 이름: {dong_name}")

        # json형태
        return jsonify({
            'success': True,
            'latitude': latitude,
            'longitude': longitude,
            'apartment_name': apartment_name,
            'direction': direction,
            'dong_name': dong_name
        })
    else:
        # 검색 결과가 없을 경우
        print(f"'{CSV_FILE}'에서 '{search_query}'에 해당하는 아파트 정보를 찾을 수 없습니다.")
        return jsonify({'success': False, 'message': '입력하신 주소/아파트명을 찾을 수 없습니다.'})

if __name__ == '__main__':
    app.run(debug=True)