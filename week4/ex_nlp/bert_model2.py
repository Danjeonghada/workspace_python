# pip install sentence-transformers
from sentence_transformers import SentenceTransformer, util
# 문장 유사도
model = SentenceTransformer('all-MiniLM-L6-v2')
sentences = [
    "나는 오늘 아침에 커피를 마셨다."
    ,"점심엔 친구랑 파스타를 먹음."
    ,"커피는 내 하루의 시작"
    ,"저녁엔 영화 한편봄."
]
sentence_embedding = model.encode(sentences, convert_to_tensor=True)
# 비교 문장
query = "하루를 커피로"
query_embedding = model.encode(query, convert_to_tensor=True)
# 유사도 계산
cos_scores = util.cos_sim(query_embedding, sentence_embedding)[0]
top_result = cos_scores.argsort(descending=True)[:3]
print(f"입력 문장:{query}\n")
print("가장 유사한 문장 top3:")
for idx in top_result:
    print(f" -{sentences[idx]} 유사도 :{cos_scores[idx]:.4f}")
