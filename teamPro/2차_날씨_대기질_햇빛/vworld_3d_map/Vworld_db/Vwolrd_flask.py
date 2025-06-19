from flask import Flask, request, render_template, jsonify
import cx_Oracle
import re

app = Flask(__name__)

# 오라클 DB 연결 정보
conn_info = {
    "user": "ef",
    "password": "ef",
    "dsn": cx_Oracle.makedsn("192.168.0.44", 1521, service_name="xe")
}

@app.route("/")
def main():
    user_id = "kwj"
    sql = """
        SELECT u.USER_ID, u.KAPT_CODE, u.USER_BLOCK, a.KAPT_NAME, b.LATITUDE, b.LONGITUDE
        FROM USER_INFO u
        LEFT JOIN APARTMENTS_ADDRESS a ON u.KAPT_CODE = a.KAPT_CODE
        LEFT JOIN APARTMENTS_BLOCK b ON u.KAPT_CODE = b.KAPT_CODE AND u.USER_BLOCK = b.APT_BLOCK
        WHERE u.USER_ID = :user_id
    """
    with cx_Oracle.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, user_id=user_id)
            row = cur.fetchone()
            if not row:
                # 기본값 (대전 시청)
                lat, lng, apt_name = 36.3504, 127.3845, "정보없음"
            else:
                lat = float(row[4]) if row[4] else 36.3504
                lng = float(row[5]) if row[5] else 127.3845
                apt_name = row[3] or "정보없음"
    return render_template("index.html", userLat=lat, userLng=lng, userAptName=apt_name)

@app.route('/autocomplete_name')
def autocomplete_name():
    term = request.args.get('term', '')
    conn = cx_Oracle.connect(**conn_info)
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT KAPT_NAME
        FROM APARTMENTS_ADDRESS
        WHERE KAPT_NAME LIKE :term
        AND ROWNUM <= 10
    """
    cursor.execute(query, term=f"%{term}%")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(names)

@app.route('/get_blocks')
def get_blocks():
    apt_name = request.args.get('apt_name', '')
    conn = cx_Oracle.connect(**conn_info)
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT b.APT_BLOCK
        FROM APARTMENTS_ADDRESS a
        JOIN APARTMENTS_BLOCK b ON a.KAPT_CODE = b.KAPT_CODE
        WHERE a.KAPT_NAME = :apt_name
    """
    cursor.execute(query, apt_name=apt_name)
    blocks = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(blocks)

@app.route('/search_address', methods=['POST'])
def search_address():
    data = request.get_json()
    name = data.get('name')
    block = data.get('block')

    try:
        conn = cx_Oracle.connect(**conn_info)
        cursor = conn.cursor()

        if block:  # 동이 있으면 BLOCK 테이블 JOIN해서 가져옴
            query = """
                SELECT b.KAPT_CODE, a.KAPT_NAME, b.APT_BLOCK,
                       b.LATITUDE, b.LONGITUDE, b.DIRECTION, a.NEW_ADDRESS
                FROM APARTMENTS_ADDRESS a
                JOIN APARTMENTS_BLOCK b ON a.KAPT_CODE = b.KAPT_CODE
                WHERE a.KAPT_NAME LIKE :name
                AND b.APT_BLOCK = :block
                AND ROWNUM = 1
            """
            cursor.execute(query, name=f"%{name}%", block=block)
            row = cursor.fetchone()
        else:  # block이 없으면 ADDRESS 테이블에서 바로 검색
            query = """
                SELECT KAPT_CODE, KAPT_NAME, NULL as APT_BLOCK,
                       LATITUDE, LONGITUDE, NULL as DIRECTION, NEW_ADDRESS
                FROM APARTMENTS_ADDRESS
                WHERE KAPT_NAME LIKE :name
                AND ROWNUM = 1
            """
            cursor.execute(query, name=f"%{name}%")
            row = cursor.fetchone()

        cursor.close()
        conn.close()

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
    app.run(debug=True)
