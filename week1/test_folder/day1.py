# 주석 Ctrl + /
print('hello') # 콘솔 프린트
# 문자열 '' or "" or '''''' or """"""
a = "hi"
print(a)
print(type(a)) # 타입 자동 인식
b = """
긴 문자열
' or " 
"""
print(b)
print(a * 100) # 문자열 곱하기 가능
# python 식별자 : 변수, 함수, 클래스, 모듈...의 이름
# 규칙
# 1. 알파벳, 숫자, 언더스코어(_)로 구성
# 2. 숫자로 시작할 수 없음
# 3. 대소문자를 구별함.
# 4. 예약어를 사용할 수 없음(for, if, while, ...)
# 보통 변수는 스네이크 표기법 사용(_)
my_var = 10
print(my_var, type(my_var))
my_var = 10.1
print(my_var, type(my_var))
flag = True
if flag:
    print("true 입니다.")
else:
    print("false 입니다.")
print("종료")
# 문자열 기본 함수
print(a.upper())
print("HELLO".lower())
c = "Life is Short".replace("Short", "Long")
print(c)
# 문자열 콘솔 입력 받기
msg = input("문자를 입력하세요!:")
print(msg, type(msg))
num = int(msg)
print(num, type(num))

