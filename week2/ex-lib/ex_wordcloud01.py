# pip install wordcloud
# pip install konlpy
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

df = pd.read_csv("../../dataset/TS/스포츠_S_TRAIN.csv", encoding="utf-8")
print(df.shape)
text_data = " ".join(df['DATA_TEXT'].dropna())
# 워드 클라우드
cloud = WordCloud(font_path="../../dataset/NanumGothicBold.ttf", width=800, height=400, background_color="white").generate(text_data)
plt.figure(figsize=(10, 5))
plt.imshow(cloud)
plt.axis("off")
plt.show()
