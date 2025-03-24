import random
import requests

def get_lotto():
    """
    로또 번호 6개 생성
    1 ~ 45 사이의 숫자
    :return: set
    """
    lotto_num = set()
    while len(lotto_num) < 6:
        lotto_num.add(random.randint(1, 45))
    return lotto_num

# 원화 to 달러
def krw_to_usd(krw):
    res = requests.get("https://open.er-api.com/v6/latest/USD")
    if res.status_code == 200:
        data = res.json()
        exchange_rate = data['rates']['KRW']
        user_usd = f"{krw}원은 : {krw / exchange_rate}달러"
    return user_usd
# 달러 to 원화 함수를 만들어 주세요.
def usd_to_krw(usd):
    res = requests.get("https://open.er-api.com/v6/latest/USD")
    if res.status_code == 200:
        data = res.json()
        exchange_rate = data['rates']['KRW']
        user_krw = f"{usd}달러는 : {usd * exchange_rate}원"
        return user_krw

# 모듈 내 실행
if __name__ == '__main__':
    print("로또 잘 생성되나")
    print(get_lotto())

if __name__ == '__main__':
    print("환율 계산")
    print(usd_to_krw(100))
    print(krw_to_usd(20000))

test = (1, 14, 15)
# to list
test2 = list(test)[:2]  # :2 <-- 처음부터 2-1 인덱스까지 슬라이싱
print(test2)
# to set
my_set = set(test2)  # 해당 데이터가 포함 되어 있는 set 생성
print(my_set, type(my_set))
# user_lotto 함수 생성
def user_lotto(*args):
    flag = True
    msg = '정상 처리!'
    # 조건 1
    for v in args:
        # if 1 > v or v > 45 :
        if not (1 <= v <= 45):
            flag = False
            msg = "1 ~ 45 사이 값만 가능"
            return flag, msg, None
# input : 0 ~ n개 (사용자 희망 번호) 가변!?
# output : true or false, 메세지, 로또 번호 (사용자 희망 번호가 포함된) 여러개!?
# 사용자가 입력한 번호를 포함 시켜서 로또 번호 생성
# 단 사용자 입력은 최대 5개 까지만 포함 슬라이싱!?
# 각 사용자 입력은 1 ~ 45 사이 수만
# 조건을 만족 하지 않으면 false, 만족 하면 true
# 메세지는 false 일 때 왜 false 인지
