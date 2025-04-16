import threading
import cx_Oracle
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 포지션 맵 정의
position_map = {
    "1": "GK", "3": "RWB", "4": "RB", "6": "CB", "8": "LB",
    "9": "LWB", "11": "CDM", "13": "RM", "15": "CM", "17": "LM",
    "19": "CAM", "22": "CF", "24": "RW", "26": "ST", "28": "LW"
}

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


def fetch_position_data(site_id):
    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={site_id}"
    res = requests.get(url, timeout=30)
    res.encoding = 'utf-8'
    return BeautifulSoup(res.text, 'html.parser')


def extract_main_positions(soup):
    pos_tags = soup.select("ul.tooltip_position span.pos")
    positions = []
    for tag in pos_tags:
        class_names = tag.get("class", [])
        pos_code = next(
            (c[3:] for c in class_names if c.startswith("pos") and c[3:].isdigit() and len(c) == 5),
            None
        )
        if pos_code and pos_code in position_map:
            positions.append(position_map[pos_code])
    return list(set(positions))


def update_main_position(card_id):
    """크롤링을 통해 메인 포지션 업데이트"""
    site_id = fix_card_id(card_id)
    soup = fetch_position_data(site_id)
    main_positions = extract_main_positions(soup)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for pos in main_positions:
            # 메인 포지션을 card_position 테이블에 업데이트
            cursor.execute("""
                UPDATE card_position
                SET main_position = 'Y'
                WHERE card_id = :card_id AND position_name = :position_name
            """, {'card_id': card_id, 'position_name': pos})

        conn.commit()
        safe_print(f"✔ 클럽 히스토리 및 메인 포지션 업데이트됨: card_id={card_id}")
    except Exception as e:
        safe_print(f"❌ 예외 발생(card_id={card_id}): {e}")
    finally:
        cursor.close()


def load_card_ids():
    conn = cx_Oracle.connect(username, password, dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM player_cards")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids


def cleanup():
    """최종 정리: 연결 종료"""
    if hasattr(thread_local, "conn"):
        thread_local.conn.close()


if __name__ == "__main__":
    card_ids = load_card_ids()
    print(f"📝 총 {len(card_ids)}개 카드 포지션 수집 시작")

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(update_main_position, card_ids), total=len(card_ids), desc="진행률"))

    cleanup()
    print("✅ 메인 포지션 업데이트 완료")
