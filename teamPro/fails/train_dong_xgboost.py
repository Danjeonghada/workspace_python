import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os

# 1. 데이터 불러오기
df = pd.read_excel("동별세대당전기요금.xlsx")

# 2. feature & target 지정
features = df[["dong", "year", "month"]]
target = df["final_monthly_fee"]

# 3. 동(dong) 컬럼 원-핫 인코딩
features = pd.get_dummies(features, columns=["dong"])
# 4. 학습 데이터 전체 사용
X = features
y = target

# 5. 모델 정의 및 학습
model = XGBRegressor(n_estimators=300, learning_rate=0.1, random_state=42)
model.fit(X, y)

# 6. 전체 데이터 예측 및 오차 확인
y_pred = model.predict(X)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))

print("✅ XGBoost 모델 학습 완료 (전체 데이터)")
print(f"📌 MAE  : {mae:.2f} 원")
print(f"📌 RMSE : {rmse:.2f} 원")

# 7. 모델 저장
os.makedirs("dong_flask/xgb_models", exist_ok=True)
joblib.dump(model, "dong_flask/xgb_models/xgb_model.pkl")
print("✅ 모델 저장: xgb_models/xgb_model.pkl")
