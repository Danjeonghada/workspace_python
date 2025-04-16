from gensim.models import Word2Vec


model = Word2Vec.load('news.model')
print(model.wv.most_similar(positive=['봉준호','영화','개봉']))
# while True:
#     text = input("검색단어")
#     print(model.wv.most_similar(positive=[text]))

