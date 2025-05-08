from youtube_util import *
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

url = "https://www.youtube.com/watch?v=0gknMu8B1J8&t=12s"
video_id = extract_id(url)
comments = get_comments(video_id, 10000)
df = pd.DataFrame(comments)
df_sorted = df.sort_values(by='like_count', ascending=False)
print(df_sorted.head(100))
fn_wordcloud('test', df_sorted)
comments_text = ' '.join(df_sorted['comment'].tolist())
wordcloud = WordCloud(width=800, height=400,background_color='white'
,font_path='../../dataset/NanumGothicBold.ttf' ).generate(comments_text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()




