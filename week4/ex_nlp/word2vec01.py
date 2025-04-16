import requests
import re
from gensim.models.word2vec import Word2Vec
# 그림 형제 동화집
# 백설공주, 신데렐라, 헨젤과 그레텔...
res = requests.get('https://www.gutenberg.org/files/2591/2591-0.txt')
grimm = res.text[2801:530661]  # 목차, 메타데이터 제외(본문만)
print(grimm)
grimm = re.sub(r'[^a-zA-Z\.]',' ', grimm)
sentence = grimm.split('. ')
data = [s.split() for s in sentence]
# print(data)
embedding_model = Word2Vec(data, sg=1           #0:CBOW, 1:skip-gram
                           , vector_size=100    # 단어 임베딩 차원
                           , window=4           # 앞뒤 단어를 얼만큼
                           , min_count=3        # 출현 최소빈도
                           , workers=4)         # 동시 처리 작업수
print("단어 연산 : king - man + woman = ?")
print(embedding_model.wv.most_similar(
        positive=['king','woman'], negative=['man']))
# king 남성 + 왕
# man을 빼면 왕 이라는 중립적 개념만 남음
# 여기에 woman을 더하면 여성 + 왕 -> queen 여왕
vocab = list(embedding_model.wv.key_to_index.keys())
while True:
    mode = input("\n 모드선택 (1:유사어, 2:반대어, 3:이상한 단어, q 종료)")
    if mode =="q":
        break
    word = input("기준 단어 입력")
    if word not in vocab:
        print("해당 단어는 없음...")
        continue
    if mode =='1':
        print(f"{word} 와 유사한 단어:")
        for w, score in embedding_model.wv.most_similar(positive=[word]):
            print(f" {w} ({score:.2f})")
    elif mode =='2':
        print(f"{word} 와 반대 의미 추정:")
        for w, score in embedding_model.wv.most_similar(negative=[word]):
            print(f" {w} ({score:.2f})")
    elif mode =='3':
        odd_one = embedding_model.wv.doesnt_match(word)
        print(" 이상한 단어:", odd_one)

