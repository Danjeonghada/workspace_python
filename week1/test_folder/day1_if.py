# 조건문 if는 조건에 따라 코드 블록을 실행
num = int(input("정수를 입력하세요:"))

if num > 10:
    print("입력은 10보다 큼")
elif num == 10:
    print("입력은 10과 같음")
elif num == 9:
    pass # 아무 작업도 하지 않을 때
else:
    print("9보다 작음")
    print("종료")