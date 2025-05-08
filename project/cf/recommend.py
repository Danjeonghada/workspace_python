import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import cx_Oracle
from sklearn.metrics.pairwise import cosine_similarity
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Oracle DB 연결
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'
conn = cx_Oracle.connect(username, password, dsn)

# 2. 데이터 불러오기
sql = """
SELECT r.MEM_ID, c.CARD_ID, r.AVERAGE_RATING,
       p.PLAYER_NAME, s.CLASS_NAME,
       p.PLAYER_NAME || ' (' || s.CLASS_NAME || ')' AS TITLE
FROM PLAYER_REVIEW r
JOIN PLAYER_CARDS c ON r.CARD_ID = c.CARD_ID
JOIN PLAYERS p ON c.PLAYER_ID = p.PLAYER_ID
JOIN SEASONS s ON c.SEASON_ID = s.SEASON_ID
WHERE r.AVERAGE_RATING IS NOT NULL
"""
df = pd.read_sql(sql, conn)
conn.close()

# 3. 사용자-선수 행렬
user_matrix = df.pivot_table(index='MEM_ID', columns='TITLE', values='AVERAGE_RATING').fillna(0)

# 4. 유사도 계산
sim_df = pd.DataFrame(
    cosine_similarity(user_matrix),
    index=user_matrix.index,
    columns=user_matrix.index
)


# 5. 추천 함수
def get_user_recommend(mem_id):
    if mem_id not in user_matrix.index:
        return []

    sim_users = sim_df[mem_id].sort_values(ascending=False).iloc[1:6].index
    my_players = set(df[df['MEM_ID'] == mem_id]['TITLE'])

    recommend = []

    for sim_user in sim_users:
        similarity = sim_df.loc[mem_id, sim_user] * 100  # 유사도 %
        top_rated = df[df['MEM_ID'] == sim_user].sort_values(by='AVERAGE_RATING', ascending=False)
        unseen = top_rated[
            (top_rated['AVERAGE_RATING'] >= 3.5) &
            (~top_rated['TITLE'].isin(my_players))
            ]

        for _, row in unseen.head(3).iterrows():
            recommend.append({
                "card_id": row['CARD_ID'],
                "title": row['TITLE'],
                "rating": float(row['AVERAGE_RATING']),
                "similarity": round(similarity, 1)
            })

    return recommend


# 6. 실행부
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용자 ID를 입력하세요")
        sys.exit(1)

    target = sys.argv[1]
    results = get_user_recommend(target)
    print(json.dumps(results, ensure_ascii=False))
