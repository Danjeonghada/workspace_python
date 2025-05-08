# pip install transformers torch
# pip install protobuf==3.20.*
from transformers import pipeline, BertTokenizer
analyzer = pipeline("sentiment-analysis")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
comments = []
while True:
    comment = input("감성 분석 문장 입력(종료:q):")
    if comment =='q':
        break
    tokens = tokenizer.tokenize(comment)
    if len(tokens) <= 512:
        comments.append(comment)
sentiments = [analyzer(comment)[0]['label']  for comment in comments]
positive_cnt = sentiments.count("POSITIVE")
negative_cnt = sentiments.count("NEGATIVE")
print(f"p:{positive_cnt}, n:{negative_cnt}")


