from sklearn.linear_model import LinearRegression
import pickle
import pandas as pd

# 파일에서 모델 로드
with open('./manhattan_model.pkl', 'rb') as f:
    model = pickle.load(f)
print(model.coef_)
print(model.intercept_)
sample = pd.DataFrame()