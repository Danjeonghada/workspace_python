import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

np.random.seed(42)
iris = load_iris()
x = iris.data
y = iris.target

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
model =DecisionTreeClassifier(criterion='entropy', random_state=42)
model.fit(x_train, y_train)
plt.figure(figsize=(16, 10))
plot_tree(model, feature_names=iris.feature_names
         ,class_names=iris.target_names, filled=True
         ,rounded=True, fontsize=10)
plt.show()