import threading
import cx_Oracle
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import time

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
failed_ids = []  # 실패한 card_id 저장용


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


def fetch_position_data(site_id, retries=3, delay=5):
    """데이터 크롤링"""
    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={site_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    for attempt in range(retries):
        try:
            res = requests.get(url, headers=headers, timeout=30)
            res.encoding = 'utf-8'
            return BeautifulSoup(res.text, 'html.parser')
        except requests.exceptions.RequestException:
            time.sleep(delay)
    raise Exception(f"[{site_id}] 요청 실패")


def extract_main_positions(soup):
    """메인 포지션 추출"""
    positions = []
    pos_tags = soup.select("ul.tooltip_position span.pos")
    for tag in pos_tags:
        class_names = tag.get("class", [])
        for class_name in class_names:
            if class_name.startswith("pos"):  # pos로 시작하는 클래스만 처리
                pos_code = class_name[3:]  # 'pos' 뒤의 숫자 추출
                if pos_code.isdigit():  # 숫자만 있는 경우
                    if pos_code in position_map:
                        positions.append(position_map[pos_code])

    return list(set(positions))


def update_main_position(card_id):
    """메인 포지션 업데이트"""
    try:
        site_id = fix_card_id(card_id)
        soup = fetch_position_data(site_id)
        main_positions = extract_main_positions(soup)

        conn = get_connection()
        cursor = conn.cursor()

        for pos in main_positions:
            cursor.execute("""
                UPDATE card_position
                SET main_position = 'Y'
                WHERE card_id = :card_id AND position_name = :position_name
            """, {'card_id': card_id, 'position_name': pos})

        conn.commit()
        safe_print(f"✔ 업데이트 완료: card_id={card_id}")
    except Exception as e:
        failed_ids.append(card_id)
        safe_print(f"❌ 실패(card_id={card_id}): {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()


def load_card_ids():
    """card_id 목록 로드"""
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


def retry_failed(ids):
    """실패한 card_id 재시도"""
    safe_print(f"🔁 실패한 {len(ids)}개 카드 재시도 시작")
    failed_final = []
    for card_id in tqdm(ids, desc="재시도 진행률"):
        try:
            update_main_position(card_id)
        except Exception:
            failed_final.append(card_id)
    if failed_final:
        with open("failed_final.txt", "w") as f:
            for fid in failed_final:
                f.write(str(fid) + "\n")
        safe_print(f"⚠ 최종 실패 {len(failed_final)}개 → failed_final.txt에 저장됨")
    else:
        safe_print("🎉 재시도 모두 성공!")


if __name__ == "__main__":
    card_ids = load_card_ids()
    print(f"📝 총 {len(card_ids)}개 카드 메인 포지션 업데이트 시작")

    # 병렬 처리
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(update_main_position, card_ids), total=len(card_ids), desc="진행률"))

    cleanup()

    if failed_ids:
        retry_failed(failed_ids)

    print("✅ 전체 작업 완료")

