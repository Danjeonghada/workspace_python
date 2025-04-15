import re

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
# pip install gensim
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
import pandas as pd
from tensorboard.compat.tensorflow_stub.tensor_shape import vector
from tensorflow import scatter_nd

plt.rcParams['font.family'] = 'Malgun Gothic'

df = pd.read_csv('../../dataset/TS/연예_E_TRAIN.csv')

def tokenize_korean(text):
    tokens = re.findall(r"[가-힣]{2,}", text)
    return tokens

# 1. word2vec 학습 문장
sentences = df['DATA_TEXT'].dropna().apply(tokenize_korean).tolist()
# 2. 모델 생성
model = Word2Vec(sentences, vector_size=100
                 ,window=2, min_count=1, sg=1)

# 임베딩 정보 저장
model.save("news.model")

# 3. 시각화를 위해 차원 축소 100 -> 3 차원으로
words = model.wv.index_to_key[:50]
vectors = [model.wv[word] for word in words]
pca = PCA(n_components=3)
reduced = pca.fit_transform(vectors)

df = pd.DataFrame(reduced, columns=["X", "Y", "2"])
df['단어'] = words

# 3d 시각화
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
xs, ys, zs = reduced[:, 0], reduced[:, 1], reduced[:, 2]
ax.scatter(xs, ys, zs)
for i, word in enumerate(words):
    ax.text(xs[i], ys[i], zs[i], word)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.tight_layout()
plt.show()

