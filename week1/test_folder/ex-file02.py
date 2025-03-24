import os

# os python 기본 라이브러리 운영체제와 상호작용 가능
# 탐색, 삭제, 변경 ...정보조회..

dir = os.getcwd() # 현재 위치
print(dir)
file_list = os.listdir(dir) # 해당 위치 파일 리스트 (폴더 작용)
for fileNm in file_list:
    print(fileNm)
    file_path = os.path.join(dir, fileNm) # 경로
    if os.path.isfile(file_path):
        print("파일!:", file_path)
        if 'main' in fileNm:

            print("main파일 삭제 !!")
            os.remove(file_path)
    elif os.path.isdir(file_path):
        print("폴더!:", file_path)
        if fileNm == 'text':
            print("text 폴더 삭제!!")
            os.rmdir(file_path)

# 폴더 생성
new_dir = 'test_folder'
if not os.path.exists(new_dir):
    os.mkdir(new_dir) # 폴더 생성

else:
    print("존재함")

# 파일 복사
import shutil
source = 'main.txt'
copy_dir = './test_folder'

copy_path = os.path.join(copy_dir, 'copy_main.txt')
shutil.copy(source, copy_path)

# 파일 이동
shutil.move(copy_path, dir)