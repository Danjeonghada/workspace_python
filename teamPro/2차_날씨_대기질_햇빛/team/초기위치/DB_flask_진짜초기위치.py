from flask import Flask, request, render_template, jsonify
import cx_Oracle
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Oracle DB 접속 정보
conn_info = {
    "user": "ef",
    "password": "ef",
    "dsn": cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
}

@app.route('/result_data')
def result_data():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id 없음'})

    sql = """
        SELECT 
            u.NICKNAME,
            COALESCE(b.LATITUDE, a.LATITUDE),
            COALESCE(b.LONGITUDE, a.LONGITUDE),
            b.DIRECTION
        FROM USER_INFO u
        LEFT JOIN APARTMENTS_ADDRESS a ON u.KAPT_CODE = a.KAPT_CODE
        LEFT JOIN APARTMENTS_BLOCK b ON u.KAPT_CODE = b.KAPT_CODE AND u.USER_BLOCK = b.APT_BLOCK
        WHERE u.USER_ID = :user_id
    """
    try:
        with cx_Oracle.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, user_id=user_id)
                row = cur.fetchone()
                if not row:
                    return jsonify({'success': False, 'message': '사용자 정보 없음'})

                nickname, lat, lng, direction = row
                return jsonify({
                    'success': True,
                    'nickname': nickname,
                    'latitude': float(lat) if lat else 37.5665,
                    'longitude': float(lng) if lng else 126.9780,
                    'direction': direction or ""
                })
    except Exception as e:
        return jsonify({'success': False, 'message': f'DB 오류: {str(e)}'})

@app.route('/autocomplete_name')
def autocomplete_name():
    term = request.args.get('term', '')
    try:
        with cx_Oracle.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT DISTINCT KAPT_NAME
                    FROM APARTMENTS_ADDRESS
                    WHERE KAPT_NAME LIKE :term AND ROWNUM <= 10
                """
                cur.execute(query, term=f"%{term}%")
                names = [row[0] for row in cur.fetchall()]
                return jsonify(names)
    except Exception as e:
        return jsonify([])

@app.route('/get_blocks')
def get_blocks():
    apt_name = request.args.get('apt_name', '')
    try:
        with cx_Oracle.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT DISTINCT b.APT_BLOCK
                    FROM APARTMENTS_ADDRESS a
                    JOIN APARTMENTS_BLOCK b ON a.KAPT_CODE = b.KAPT_CODE
                    WHERE a.KAPT_NAME = :apt_name
                """
                cur.execute(query, apt_name=apt_name)
                blocks = [row[0] for row in cur.fetchall()]
                return jsonify(blocks)
    except Exception as e:
        return jsonify([])

@app.route('/search_address', methods=['POST'])
def search_address():
    data = request.get_json()
    name = data.get('name')
    block = data.get('block')

    try:
        with cx_Oracle.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                if block:
                    query = """
                        SELECT b.KAPT_CODE, a.KAPT_NAME, b.APT_BLOCK,
                               b.LATITUDE, b.LONGITUDE, b.DIRECTION, a.NEW_ADDRESS
                        FROM APARTMENTS_ADDRESS a
                        JOIN APARTMENTS_BLOCK b ON a.KAPT_CODE = b.KAPT_CODE
                        WHERE a.KAPT_NAME LIKE :name AND b.APT_BLOCK = :block AND ROWNUM = 1
                    """
                    cur.execute(query, name=f"%{name}%", block=block)
                    row = cur.fetchone()
                else:
                    query = """
                        SELECT KAPT_CODE, KAPT_NAME, NULL as APT_BLOCK,
                               LATITUDE, LONGITUDE, NULL as DIRECTION, NEW_ADDRESS
                        FROM APARTMENTS_ADDRESS
                        WHERE KAPT_NAME LIKE :name AND ROWNUM = 1
                    """
                    cur.execute(query, name=f"%{name}%")
                    row = cur.fetchone()

                if row:
                    _, apt_name, apt_block, lat, lng, direction, address = row
                    match = re.search(r"(\S+동)", address) if address else None
                    dong_name = match.group(1) if match else "정보 없음"
                    full_name = f"{apt_name} {apt_block}" if apt_block else apt_name
                    return jsonify({
                        'success': True,
                        'latitude': lat,
                        'longitude': lng,
                        'apartment_name': full_name,
                        'direction': direction if direction else "",
                        'dong_name': dong_name
                    })
                else:
                    return jsonify({'success': False, 'message': '검색 결과 없음'})
    except Exception as e:
        print("[DB 에러]", e)
        return jsonify({'success': False, 'message': '서버 오류 발생'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
