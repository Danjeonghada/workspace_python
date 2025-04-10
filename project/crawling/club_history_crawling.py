import threading
import cx_Oracle
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 스레드 로컬 저장소
thread_local = threading.local()
print_lock = threading.Lock()  # 출력 동기화용


def get_connection():
    """각 스레드마다 독립적인 데이터베이스 연결"""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn


def safe_print(*args, **kwargs):
    """출력 동기화"""
    with print_lock:
        print(*args, **kwargs)


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


def process_club_history(card_id):
    """클럽 히스토리 데이터 추출 및 player_club_history 테이블에 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    fixed_card_id = fix_card_id(card_id)

    # player_id는 card_id에서 뒤의 6자리를 추출하여 설정
    player_id = str(fixed_card_id)[-6:]

    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={fixed_card_id}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            safe_print(f"❌ 요청 실패: {url}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # 클럽 히스토리 데이터 추출
        club_history_section = soup.find('div', class_='fifa4 player_club clearfix')
        if club_history_section:
            for item in club_history_section.find_all('li', class_='fifa4 clearfix'):
                year_range = item.find('span').text.strip()
                club_name = item.text.replace(year_range, '').strip()

                # 연도 범위 처리 (끝 연도 없으면 None으로 처리)
                start_year, end_year = year_range.split('~')
                start_year = int(start_year.strip())
                end_year = None if end_year.strip() == '' else int(end_year.strip())

                # 클럽 ID 가져오기
                cursor.execute("SELECT club_id FROM clubs WHERE club_name = :1", [club_name.strip()])
                club_result = cursor.fetchone()
                if club_result:
                    club_id = club_result[0]
                    cursor.execute("""
                        INSERT INTO player_club_history (player_id, club_id, start_year, end_year)
                        VALUES (:player_id, :club_id, :start_year, :end_year)
                    """, {'player_id': player_id, 'club_id': club_id, 'start_year': start_year, 'end_year': end_year})
                    safe_print(f"✔ 클럽 히스토리 업데이트됨: card_id={card_id}, club={club_name}, {start_year}~{end_year}")
                else:
                    safe_print(f"⚠ 클럽 없음: {club_name}")

        conn.commit()

    except Exception as e:
        safe_print(f"❌ 클럽 히스토리 예외 발생(card_id={card_id}): {e}")

    finally:
        cursor.close()


def cleanup():
    """최종 정리: 연결 종료"""
    if hasattr(thread_local, "conn"):
        thread_local.conn.close()


if __name__ == '__main__':
    # 카드 ID 목록 가져오기
    conn = cx_Oracle.connect(username, password, dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM player_cards")
    card_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # 클럽 히스토리 업데이트 병렬 실행
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(process_club_history, card_ids), total=len(card_ids), desc="클럽 히스토리 진행률"))

    cleanup()
    safe_print("✅ 전체 업데이트 완료")
