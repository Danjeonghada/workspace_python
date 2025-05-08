import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

np.random.seed(42)
wine = load_wine()
x = wine.data
y = wine.target

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
# 트리의 최대 깊이를 제한하여 너무 깊어지는 것을 방지함.
model =DecisionTreeClassifier(criterion='gini',max_depth=3, random_state=42)
model.fit(x_train, y_train)
plt.figure(figsize=(16, 10))
plot_tree(model, feature_names=wine.feature_names, class_names=wine.target_names
          , filled=True, rounded=True, fontsize=10)
plt.show()
acc = model.score(x_test, y_test)
print(f"모델 정확도:{acc:.2f}")
# 0 : 바롤로, 1:그라뇰라노, 2:바르베리