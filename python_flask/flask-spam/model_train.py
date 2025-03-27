import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

df = pd.read_excel("../../dataset/korean_emails.xlsx")
texts = df['message']
labels = df['gubun']

# 벡터화
vectorizer = CountVectorizer()
x = vectorizer.fit_transform(texts)
print(x)
x_train, x_test, y_train, y_test = train_test_split(x, labels, test_size=0.2)
# 모델 학습
model = LogisticRegression()
model.fit(x_train, y_train)
# 평가
y_pred = model.predict(x_test)
print("정확도:", accuracy_score(y_test, y_pred))

# 저장
with open("spam_model.pkl", "wb") as f:
    pickle.dump(model, f)
# 단어 정보
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
print("저장 완료")
