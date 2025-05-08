from youtube_util import *
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from transformers import pipeline, BertTokenizer

analyzer = pipeline("sentiment-analysis")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template('index.html')
@app.route("/analyze", methods=['POST'])
def analyze():
    youtube_url = request.form.get("youtube_url")
    video_id = extract_id(youtube_url)
    if video_id:
        comments = get_comments(video_id, 50)
        comments_data = pd.DataFrame(comments)
        img_path = fn_wordcloud(video_id,comments_data)
        # 감성분석
        comment_list = comments_data['comment'].tolist()
        sentiements = [analyzer(comment)[0]['label'] for comment in comment_list ]
        positive_cnt = sentiements.count('POSITIVE')
        negative_cnt = sentiements.count("NEGATIVE")
        return jsonify({"word_url":img_path,
                        "p_cnt":positive_cnt,
                        "n_cnt":negative_cnt,
                        "p_comment":[comment_list[i]
                           for i in range(len(comment_list)) if sentiements[i] =="POSITIVE"],
                        "n_comment":[comment_list[i]
                           for i in range(len(comment_list)) if sentiements[i] =="NEGATIVE"]
                        })
    return jsonify({'error': 'invalid youtube URL'}), 400


if __name__ == '__main__':
    app.run(debug=True)