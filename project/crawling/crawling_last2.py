import cx_Oracle
import requests
from bs4 import BeautifulSoup
import threading
import re
from tqdm import tqdm

# DB 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 스레드별 DB 연결
thread_local = threading.local()

def get_connection():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn

# 카드 ID 변환 (사이트용)
def fix_card_id(card_id):
    card_id = str(card_id)
    prefix = card_id[:3]
    suffix = card_id[3:]

    if prefix == '212':
        return int('203' + suffix)
    elif prefix == '234':
        return int('224' + suffix)
    else:
        return int(card_id)

# HTML 크롤링 후 데이터 추출
def extract_player_info(for_site_card_id):
    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={for_site_card_id}"
    res = requests.get(url, timeout=10)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    height = weight = body_type = None
    body_tag = next((li for li in soup.select("ul.fifa4.state.clearfix li") if "cm" in li.text and "kg" in li.text), None)

    if body_tag:
        parts = body_tag.text.strip().split("/")
        if len(parts) == 3:
            h = re.search(r"(\\d+)", parts[0])
            w = re.search(r"(\\d+)", parts[1])
            if h: height = h.group(1)
            if w: weight = w.group(1)
            body_type = parts[2].strip()

    skill_moves = len(soup.select("li.star_area p.star.act"))
    foot = 'L' if soup.select_one("p.foot.left.act") else 'R'
    left_foot = soup.select_one("p.foot.left")
    right_foot = soup.select_one("p.foot.right")
    left_value = int(left_foot.text.strip()) if left_foot else None
    right_value = int(right_foot.text.strip()) if right_foot else None
    salary_tag = soup.select_one("div.salary > div.bg")
    salary = int(salary_tag.text.strip()) if salary_tag else None

    return {
        'height': height,
        'weight': weight,
        'body_type': body_type,
        'skill_moves': skill_moves,
        'foot': foot,
        'left_foot': left_value,
        'right_foot': right_value,
        'salary': salary
    }

# 개별 실패 카드 재처리
def process_failed_card(original_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        fixed_id = fix_card_id(original_id)
        info = extract_player_info(fixed_id)
        info['card_id'] = original_id  # DB 기준 ID는 원래 ID 사용

        cursor.execute("""
            UPDATE player_cards
            SET height = :height, weight = :weight, body_type = :body_type,
                skill_moves = :skill_moves, foot = :foot,
                left_foot = :left_foot, right_foot = :right_foot, salary = :salary
            WHERE card_id = :card_id
        """, info)

        conn.commit()
        print(f"✔ 재처리 완료 card_id={original_id} (사이트용: {fixed_id})")

    except Exception as e:
        print(f"❌ 재처리 실패 card_id={original_id}: {e}")
    finally:
        cursor.close()

# 실패 카드 ID 로드
def load_failed_cards(path="failed_cards.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

if __name__ == "__main__":
    failed_ids = load_failed_cards()
    print(f"🔁 {len(failed_ids)}개 카드 재처리 시작...")
    for cid in tqdm(failed_ids, desc="재처리 진행률"):
        process_failed_card(cid)
    print("✅ 재처리 전체 완료")
