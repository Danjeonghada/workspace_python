import pandas as pd
import numpy as np

path = "./dataset/items_user.xlsx"
df = pd.read_excel(path, sheet_name="item_table")
history = pd.read_excel(path, sheet_name="purchase_history")

print(df.head())
# 범주형 처리
df_enc = pd.get_dummies(df, columns=["color"])
# 구간화 및 이진화(무게, 크기, 가격)
df_enc["light"] = df["weight"] <= 200
df_enc["heavy"] = df["weight"] > 200
df_enc["small"] = df["item_size"] <=95
df_enc["big"] = df["item_size"] > 95
df_enc["low"] = df["price"] <=50000
df_enc["medium"] = (df["price"] > 50000) & (df["price"] <= 500000)
df_enc["high"] = df["price"] > 500000
print(df_enc.head())
item_profile = df_enc.drop(columns=['item_id', "weight","item_size","price"])
item_profile = item_profile.astype(int)
item_profile.index = df["item_id"]
print(item_profile.head())
# 유저 프로파일 데이터
user_items = history[history['mem_id'] == "user1"]["item_id"]
# 고객이 구매한 상품 프로파일 데이터의 평균
user_profile = item_profile.loc[user_items].mean()
print(user_profile.round(2))

# 코사인 유사도
def cos_sim(x, y):
    return np.dot(x, y) /  (np.linalg.norm(x) * np.linalg.norm(y))

# 고객 정보와 모든 아이템 유사도 계산
unseen_items = item_profile.drop(index=user_items) # 구매 아이템은 제외
similarities = unseen_items.apply(lambda x:cos_sim(user_profile, x), axis=1)
similarities = similarities.round(3)
print(similarities)
# 유사도 기준 추천 top3
recommend = similarities.sort_values(ascending=False).head(3)
print(recommend)