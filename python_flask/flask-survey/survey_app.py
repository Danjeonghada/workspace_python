from flask import Flask, render_template, request, redirect, url_for
import cx_Oracle
from collections import defaultdict

app = Flask(__name__)

def get_db_conn():
    return cx_Oracle.connect("jdbc", "jdbc", "127.0.0.1:1521/xe")

@app.route('/', methods=["GET", "POST"])
def survey():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
       SELECT a.q_id
            , a.q_content
            , b.o_id
            , b.o_content
        FROM questions a
            ,q_options b
        WHERE a.q_id = b.q_id   
        ORDER BY a.q_id, b.o_id 
    """)
    # 질문 별로 보기 틀을 묶기 위한 딕셔너리 생성
    survey_data = defaultdict(lambda : {"q_content":"", "options": [] })
    rows = cursor.fetchall()
    for q_id, q_text, o_id, o_text in rows:
        survey_data[q_id]["q_content"] = q_text
        survey_data[q_id]["options"].append(
            {"o_id": o_id, "o_content" : o_text})

    # POST 일 경우
    if request.method == "POST":
        user_id = request.form['user_id']
        # 기존 응답 삭제 후 처리
        cursor.execute("DELETE FROM q_result WHERE user_id = :1", [user_id])
        # 질문별 응답 저장
        for q_id in survey_data:
            o_id = int(request.form.get(f'q{q_id}'))
            cursor.execute("INSERT INTO q_result(user_id, q_id, o_id) VALUES(:1, :2, :3)"
                          ,[user_id, q_id, o_id])
        conn.commit()
        return redirect(url_for('recommend', user_id=user_id))

    cursor.close()
    conn.close()
    return render_template('index.html', survey_data=survey_data)

# 유사 사용자 추천
@app.route("/recommend/<user_id>")
def recommend(user_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    # 전체 응답 데이터 가져오기
    cursor.execute("SELECT user_id, q_id, o_id FROM q_result")
    rows = cursor.fetchall()
    # 사용자 별 응답 전처리
    user_answers = defaultdict(dict)
    for u, q, o in rows:
        user_answers[u][q] = o
        # 추천 대상 사용자 응답
        target = user_answers[user_id]
    # 유사도 계산
    def calc_similarity(user_a, user_b):
        # 공통 질문 응답
        common = set(user_a.keys()) & set(user_b.keys())
        if not common:
            return 0
        same = sum(1 for q in common if user_a[q] == user_b[q])
        return same / len(common)

    similarities = []
    for other_user, answers in user_answers.items():
        if other_user == user_id:
            continue
        sim = calc_similarity(target, answers)
        similarities.append((other_user, sim))
    # 유사도 높은 순으로 정렬
    similarities.sort(key=lambda x: -x[1]) # 내림차순 정렬
    cursor.close()
    conn.close()
    return render_template("result.html"
                , user_id=user_id, similarities=similarities)

if __name__ == '__main__':
    app.run(debug=True)