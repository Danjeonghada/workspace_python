# while 조건식 : 조건 식이 True 면 반복
i = 1
while i <= 5:
    i += 1
    if i == 3:
        continue  # 하위 내용을 건너뜀
        # break   # 즉시 반복문 종료
    print(i)
flag = True
while flag:
    msg = input("종료(q):")
    if msg == 'q':
        flag = False