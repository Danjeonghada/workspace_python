import requests
from bs4 import BeautifulSoup


def fix_card_id(card_id):
    """card_id 바꿔주는 함수"""
    card_id = str(card_id)
    prefix = card_id[:3]
    suffix = card_id[3:]
    if prefix == '212':
        return int('203' + suffix)
    elif prefix == '234':
        return int('224' + suffix)
    return int(card_id)


def test_club_history(card_id):
    """클럽 히스토리 데이터 추출 테스트"""
    fixed_card_id = fix_card_id(card_id)
    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={fixed_card_id}"

    try:
        # URL에 요청을 보내고 페이지 소스를 받아옵니다
        response = requests.get(url)

        # 응답 상태 코드 확인
        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 클럽 히스토리 데이터 추출
        club_history_section = soup.find('div', class_='fifa4 player_club clearfix')
        if club_history_section:
            for item in club_history_section.find_all('li', class_='fifa4 clearfix'):
                year_range = item.find('span').text.strip()
                club_name = item.text.replace(year_range, '').strip()
                start_year, end_year = map(int, year_range.split('~'))
                print(f"클럽 이름: {club_name}, 시작 연도: {start_year}, 종료 연도: {end_year}")
        else:
            print("클럽 히스토리 정보가 없습니다.")

    except Exception as e:
        print(f"❌ 데이터 추출 실패 (card_id={card_id}): {e}")


# 테스트할 card_id 입력
test_club_history(825001397)  # card_id를 원하는 값으로 입력
