import os
img_dir = './고래상어'
# 너무 작은 이미지 삭제
for filename in os.listdir(img_dir):
    filepath = os.path.join(img_dir, filename)
    if os.path.isfile(filepath):
        size = os.path.getsize(filepath)
        print(size)
        if size < 1000:
            print(f'delete: {filepath}')
            os.remove(filepath)