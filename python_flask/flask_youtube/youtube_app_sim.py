from youtube_util import *
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
model = SentenceTransformer('all-MiniLM-L6-v2')
app = Flask(__name__)
CORS(app)
@app.route("/analyze", methods=["GET"])
def similarity():
    return render_template("analysis.html")
@app.route("/analyze_sim", methods=["POST"])
def analysis_similarity():
    youtube_url = request.form.get("video_id")
    video_id = extract_id(youtube_url)
    comments = get_comments(video_id, 100)
    df = pd.DataFrame(comments)
    df_sorted = df.sort_values(by="like_count", ascending=False)
    comment_list = df_sorted['comment'].tolist()
    if len(comment_list) < 2:
        return jsonify({"error": "댓글이 충분하지 않음.."})
    top_comment = comment_list[0]
    others = comment_list[1:]
    query_embedding = model.encode(top_comment, convert_to_tensor=True)
    sentence_embedding = model.encode(others, convert_to_tensor=True)
    # 유사도 계산
    cos_scores = util.cos_sim(query_embedding, sentence_embedding)[0]
    top_k = torch.topk(cos_scores, k=min(10, len(others)))
    similar = [{"comment": others[idx], "score": float(score)}
               for idx, score in zip(top_k.indices, top_k.values)]
    return jsonify({"top_comment":top_comment, "similar":similar})



if __name__ == '__main__':
    app.run(debug=True)