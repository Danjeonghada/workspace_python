import pandas as pd
from week2.ex_db.DBManager import DBManager
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
sql = """
    SELECT *
    FROM stock_bbs
"""
db = DBManager()
okt = Okt()
conn = db.get_connection()
df = pd.read_sql(con=conn, sql=sql)
nouns = []
stop_words = {"언제", "오늘", "다시", "답글", "계속", "매일"}
for idx, row in df.iterrows():
    # 1. 명사 추출
    text = row['TITLE'].strip()
    word_list = okt.nouns(text) # 명사만 추출
    filter_list = [x for x in word_list if len(x) > 1 and x not in stop_words]
    nouns += filter_list
# 2. 단어 카운트 생성
count = Counter(nouns)
print(count)

# 3. 워드클라우드 생성
cloud = WordCloud(font_path="../../dataset/NanumGothicBold.ttf", width=800, height=400, background_color="white", min_font_size=15).generate_from_frequencies(count)
plt.figure(figsize=(10, 5))
plt.imshow(cloud)
plt.axis("off")
plt.show()

