import numpy as np
# pip install wordcloud
# pip install konlpy
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
from PIL import Image
df = pd.read_csv("../../dataset/TS/연예_E_TRAIN.csv", encoding="utf-8")
df_23 = df[df['PUBDATE'].astype(str).str.startswith("2023")] # 2023xxxx
okt = Okt()
nouns = []
# 마스크 이미지
icon = Image.open("../../dataset/heart.png")
mask = Image.new("RGB", icon.size, (255, 255, 255))
mask = np.array(mask)
stop_words = {"개봉", "앨범", "지난", "통해", "오후", "이번", "공개", "기록", "발매", "차트"} # 제외 단어 목록
for idx, row in df_23.iterrows():
    text = row['DATA_TEXT'].strip()
    word_list = okt.nouns(text) # 명사만 추출
    filter_list = [x for x in word_list if len(x) > 1 and x not in stop_words]
    nouns += filter_list
count = Counter(nouns)
print(count)

# 워드 클라우드
cloud = WordCloud(font_path="../../dataset/NanumGothicBold.ttf"
                  , width=800, height=400, background_color="white"
                  , mask=mask, contour_color="black"
                  , min_font_size=15) # 최소 폰트 크기
gen = cloud.generate_from_frequencies(count)
plt.figure(figsize=(10, 5))
plt.imshow(gen)
plt.axis("off")
plt.show()
