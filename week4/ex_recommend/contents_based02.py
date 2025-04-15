import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

songs = pd.read_csv("./dataset/sample_100_songs.csv")
users = pd.read_csv("./dataset/users.csv")
print(songs.head())
print(users.head())
# 전처리
songs['idx'] = songs.index
songs['mood'] = songs['mood'].fillna('').apply(lambda x:x.split(','))
songs['instrument'] = songs['instrument'].fillna('').apply(lambda  x:x.split(','))
# 0 or 1 원핫 인코딩 처리
moods_dummies = pd.get_dummies(songs.explode('mood')[['idx','mood']]).groupby('idx').max()
instr_dummies = pd.get_dummies(songs.explode('instrument')[['idx', 'instrument']]).groupby('idx').max()
other_dummies = pd.get_dummies(songs[['genre', 'tempo','vocal','year']])
meta = songs[['song_id', 'title']]
# 노래 프로파일 데이터
song_vectors= pd.concat([meta, other_dummies, moods_dummies, instr_dummies], axis=1)
song_vectors = song_vectors.set_index('song_id')
print(song_vectors)

# 유저
user_id = 'user1'
user_row = users[users['user_id'] == user_id]
liked_songs = user_row.iloc[0]['liked_songs'].split(',')
# 유저 프로파일
liked_vectors = song_vectors.loc[liked_songs].drop(columns=['title'], errors='ignore')
user_vec = liked_vectors.mean().values.reshape(1, -1)
print(user_vec)
# 좋아요에 없던 노래를 대상으로 유사도 계산
candidate_df = song_vectors.drop(index=liked_songs, errors='ignore')
candidate_vector = candidate_df.drop(columns=['title'], errors='ignore').values
sims = cosine_similarity(user_vec, candidate_vector).flatten()
candidate_df = candidate_df.copy()
candidate_df['similarity'] = sims
# 상위 5곡
top5 = candidate_df.sort_values(by='similarity', ascending=False).head(5)
print(top5)
