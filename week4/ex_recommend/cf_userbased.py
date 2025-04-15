import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 협업 필터링 - 유저 기반
# 유사한 유저를 찾아서 유사한 유저의 아이템 정보 활용
# 모든 유저를 동일 차원으로 만들어야함.
df_ratings = pd.read_csv('./dataset/ratings.csv')
df_movies = pd.read_csv('./dataset/movies.csv')
df_ratings.drop('timestamp', axis=1, inplace=True)
user_itme_rating = pd.merge(df_ratings, df_movies, on='movieId')
user_matrix = user_itme_rating.pivot_table("rating", index="userId", columns="title")
print(user_matrix)
user_matrix.fillna(0, inplace=True)
user_cf = cosine_similarity(user_matrix)
result = pd.DataFrame(data=user_cf, index=user_matrix.index, columns=user_matrix.index)
print(result.head())
# 타겟 유저와 유사한 유저의 평점 높은 영화 5개
# 타겟 유저가 보지 않은 영화 중
def get_user(id, userId):
    movie_arr = user_itme_rating[user_itme_rating['userId'] == id]
    user_watch_movie = user_itme_rating[user_itme_rating['userId'] == userId]
    # ~ 제외의 의미
    movie_arr = movie_arr[~movie_arr['movieId'].isin(
                    user_watch_movie['movieId'].values.tolist())]
    five_movie = movie_arr.sort_values(by='rating', ascending=False).head(5)
    return five_movie['title'].values.tolist()
def get_user_item(id):
    target_best = user_itme_rating[user_itme_rating['userId'] == id].sort_values(
                                by='rating', ascending=False).head(5)
    print("target_user best 5")
    print(target_best['title'])
    sim_user = result[id].sort_values(ascending=False).head(5)
    ids = sim_user.index.tolist()[1:]
    print("sim user list", ids)
    movie_list = []
    for sim in ids:
        item = get_user(sim, id)
        movie_list = movie_list + item
    return set(movie_list) # 중복 제거
while True:
    target_id = input("추천 대상 유저 id:")
    movies = get_user_item(int(target_id))
    print("추천 영화")
    for item in movies:
        print(item)

