import random

# 업다운 게임
# 3번의 기회
# 사용자 입력이 맞으면 '정답', 작으면 '업', 크면 '다운' 출력
# 틀릴때 마다 몇번의 기회가 있는 지 출력
# computer의 랜덤 값은 1 ~ 10 사이의 정수
print("********** 업다운 게임 **********")
number = random.randint(1, 10)
chance = 3
for i in range(3):
    user = int(input("1 ~ 10 사이의 정수를 입력하세요:"))
    if user == number:
        print("정답입니다.")
        break
    elif user < number:
        print("업!!")
    elif user > number:
        print("다운!!")
    chance -= 1
    print("남은 기회 " + str(chance))
else:
    print("다음 기회에... 정답은: " + str(number))

com = random.randint(1, 10)
cnt = 3
while cnt > 0:
    user_num = int(input("1 ~ 10 사이의 정수를 입력하세요"))
    if user_num == com:
        print("정답입니다.")
        break
    elif user_num < com:
        print("업!!")
    elif user_num > com:
        print("다운!!")
    cnt -= 1
    if cnt != 0:
        print("남은 기회 " + str(chance))
    else:
        print("다음 기회에... 정답은: " + str(number))