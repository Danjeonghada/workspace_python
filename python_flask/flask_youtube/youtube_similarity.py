from youtube_util import *
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')
youtube_url = "https://www.youtube.com/watch?v=LfwWNSsMJgg&t=1724s"
video_id = extract_id(youtube_url)
comments = get_comments(video_id, 100)
df = pd.DataFrame(comments)
df_sorted = df.sort_values(by="like_count", ascending=False)
comment_list = df_sorted['comment'].tolist()
if len(comment_list) < 2:
    print("댓글이 충분하지 않음")
top_comment = comment_list[0]
others = comment_list[1:]
query_embedding = model.encode(top_comment, convert_to_tensor=True)
sentence_embedding = model.encode(others, convert_to_tensor=True)
# 유사도 계산
cos_scores = util.cos_sim(query_embedding, sentence_embedding)[0]
print(cos_scores)
top_k = torch.topk(cos_scores, k=min(10, len(others)))
similar = [{"comment":others[idx], "score": float(score)}
            for idx, score in zip(top_k.indices, top_k.values)]
print(similar)
