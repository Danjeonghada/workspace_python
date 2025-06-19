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

@app.route('/')
def index():
    return render_template('index.html')

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
        cursor.close()
        conn.close()

        if row:
            _, apt_name, apt_block, lat, lng, direction, address = row
            match = re.search(r"(\S+동)", address)
            dong_name = match.group(1) if match else "정보 없음"
            return jsonify({
                'success': True,
                'latitude': lat,
                'longitude': lng,
                'apartment_name': f"{apt_name} {apt_block}",
                'direction': direction,
                'dong_name': dong_name
            })
        else:
            return jsonify({'success': False, 'message': '검색 결과 없음'})

    except Exception as e:
        print("[DB 에러]", e)
        return jsonify({'success': False, 'message': '서버 오류 발생'})

if __name__ == '__main__':
    app.run(debug=True)
