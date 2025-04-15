import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 협업 필터링 - 유저 기반
# 유사한 유저를 찾아서 유사한 유저의 아이템 정보 활용
# 모든 유저를 동일 차원으로 만들어야함.
df_ratings = pd.read_csv('./dataset/ratings.csv')
df_movies = pd.read_csv('./dataset/movies.csv')
df_ratings.drop('timestamp', axis=1, inplace=True)
user_item_rating = pd.merge(df_ratings, df_movies, on='movieId')
movie_matrix = user_item_rating.pivot_table('rating', index="title", columns="userId")
print(movie_matrix)
movie_matrix.fillna(0, inplace=True)
# 유사도 비교
item_cf = cosine_similarity(movie_matrix)
result = pd.DataFrame(data=item_cf, index=movie_matrix.index, columns=movie_matrix.index)

def get_item_based(title):
    return result[title].sort_values(ascending=False)[:10]
while True:
    text = input("좋아하는 영화 이름을 입력하세요:")
    recommend_list = get_item_based(text)
    print(recommend_list)