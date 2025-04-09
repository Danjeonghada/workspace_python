import cx_Oracle
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import threading
import re

# DB 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 스레드별 저장소
thread_local = threading.local()
print_lock = threading.Lock()
commit_lock = threading.Lock()
commit_counter = 0

def get_connection():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def extract_player_info(card_id):
    url = f"https://fifaonline4.inven.co.kr/dataninfo/player/?code={card_id}"
    res = requests.get(url, timeout=10)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    height = weight = body_type = None
    body_tag = next(
        (li for li in soup.select("ul.fifa4.state.clearfix li") if "cm" in li.text and "kg" in li.text),
        None
    )

    if body_tag:
        parts = body_tag.text.strip().split("/")
        if len(parts) == 3:
            height_match = re.search(r"(\d+)", parts[0])
            weight_match = re.search(r"(\d+)", parts[1])
            if height_match:
                height = height_match.group(1)
            if weight_match:
                weight = weight_match.group(1)
            body_type = parts[2].strip()
    else:
        safe_print(f"⚠ 키/몸무게/체형 누락(card_id={card_id})")

    # 개인기
    skill_moves = len(soup.select("li.star_area p.star.act"))

    # 주발
    foot = 'L' if soup.select_one("p.foot.left.act") else 'R'

    # 숙련도
    left_foot = soup.select_one("p.foot.left")
    right_foot = soup.select_one("p.foot.right")
    left_value = int(left_foot.text.strip()) if left_foot else None
    right_value = int(right_foot.text.strip()) if right_foot else None

    # 급여
    salary_tag = soup.select_one("div.salary > div.bg")
    salary = int(salary_tag.text.strip()) if salary_tag else None

    return {
        'card_id': card_id,
        'height': height,
        'weight': weight,
        'body_type': body_type,
        'skill_moves': skill_moves,
        'foot': foot,
        'left_foot': left_value,
        'right_foot': right_value,
        'salary': salary
    }

def process_card(card_id):
    global commit_counter
    conn = get_connection()
    cursor = conn.cursor()

    try:
        info = extract_player_info(card_id)

        cursor.execute("""
            UPDATE player_cards
            SET height = :height, weight = :weight, body_type = :body_type,
                skill_moves = :skill_moves, foot = :foot,
                left_foot = :left_foot, right_foot = :right_foot, salary = :salary
            WHERE card_id = :card_id
        """, info)

        with commit_lock:
            commit_counter += 1
            if commit_counter % 100 == 0:
                conn.commit()
                safe_print(f"💾 {commit_counter}개 커밋 완료")

        safe_print(f"✔ card_id={card_id} → 급여:{info['salary']}, 개인기:{info['skill_moves']}")


    except Exception as e:

        safe_print(f"❌ 오류(card_id={card_id}): {e}")

        with open("failed_cards.txt", "a", encoding="utf-8") as f:

            f.write(f"{card_id}\n")
    finally:
        cursor.close()

def cleanup():
    if hasattr(thread_local, "conn"):
        thread_local.conn.commit()
        thread_local.conn.close()

if __name__ == '__main__':
    conn = cx_Oracle.connect(username, password, dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM player_cards WHERE height IS NULL")
    card_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(process_card, card_ids), total=len(card_ids), desc="진행률"))

    cleanup()
    safe_print("✅ 전체 완료")

