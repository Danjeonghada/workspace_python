import pandas as pd
import re
import numpy as np
import os
import pickle
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 데이터 로드
train_data = pd.read_csv('./naver_movie/ratings_train.txt', sep="\t")
test_data = pd.read_csv('./naver_movie/ratings_test.txt', sep="\t")
# 결축치 밎 중복 제거
train_data.dropna(inplace=True)
test_data.dropna(inplace=True)
train_data.drop_duplicates(subset=['document'],inplace=True)

# 불용어
stopwords = ['은', '는', '의', '가', '아', '좀', '잘', '강', '를']
okt = Okt()
def preprocess_text(text):
    text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]','',text) # 한글과 공백 빼고 제외
    tokens = okt.morphs(text, stem=True)
    return [word for word in tokens if word not in stopwords]
# print(preprocess_text("Hello ! 안녕ㅋㅋ 팽수가"))
train_data['tokenized'] = train_data['document'].apply(preprocess_text)
test_data['tokenized'] = test_data['document'].apply(preprocess_text)
# 정수 인코딩
# 텍스트를 -> 숫자로
tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_data['tokenized'])

x_train = tokenizer.texts_to_sequences(train_data['tokenized'])
x_test = tokenizer.texts_to_sequences(train_data['tokenized'])
# 패딩 (전체 쵀대 길이를 100으로)
max_len = 100
x_train = pad_sequences(x_train, maxlen=max_len)
x_test = pad_sequences(x_test, maxlen=max_len)
y_train = train_data['label'].values
y_test = test_data['label'].values
# 저장
save_dir = 'naver_data'
os.makedirs(save_dir, exist_ok=True)
np.save(os.path.join(save_dir, 'x_train.npy'), x_train)
np.save(os.path.join(save_dir, "x_test.npy"), x_test)
np.save(os.path.join(save_dir, "y_train.npy"), y_train)
np.save(os.path.join(save_dir, "y_test.npy"), y_test)
# tokenizer, meta info, corpus 저장
with open(os.path.join(save_dir, "tokenizer.pkl"), 'wb') as f:
    pickle.dump(tokenizer, f)
with open(os.path.join(save_dir, "meta_info.txt"),
          'w', encoding='utf-8') as f:
    f.write(f"max_len{max_len}\n")
    f.write(f"vocab_size={len(tokenizer.word_index)+1}\n")
with open(os.path.join(save_dir, "tokenized_corpus.txt"), 'w', encoding='utf-8') as f:
    for tokens in train_data['tokenized']:
        f.write("".join(tokens) + "\n")
