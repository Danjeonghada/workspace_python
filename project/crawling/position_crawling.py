import cx_Oracle
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading

username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

position_map = {
    "1": "GK", "3": "RWB", "4": "RB", "6": "CB", "8": "LB",
    "9": "LWB", "11": "CDM", "13": "RM", "15": "CM", "17": "LM",
    "19": "CAM", "22": "CF", "24": "RW", "26": "ST", "28": "LW"
}

thread_local = threading.local()
log_lock = threading.Lock()

def get_connection():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn

def log_failed(card_id, error):
    with log_lock:
        with open("failed_positions.txt", "a", encoding="utf-8") as f:
            f.write(f"{card_id} // {error}\n")

def fix_card_id(card_id):
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
    res = requests.get(url, timeout=10)
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

def extract_position_overalls(soup):
    overalls = []
    for p in soup.select("div.fifa4.field_area div.fifa4.field p"):
        pos = p.get("data-position")
        score = p.get("data-ori")

        if pos and score and score.isdigit():
            overalls.append((pos.upper(), int(score)))
    return overalls

def save_to_db(card_id, main_positions, position_overalls):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for pos in main_positions:
            cursor.execute("""
                MERGE INTO main_positions t
                USING (SELECT :card_id AS card_id, :pos AS main_position FROM dual) s
                ON (t.card_id = s.card_id AND t.main_position = s.main_position)
                WHEN NOT MATCHED THEN
                  INSERT (card_id, main_position)
                  VALUES (s.card_id, s.main_position)
            """, {'card_id': card_id, 'pos': pos})

        for pos, rating in position_overalls:
            cursor.execute("""
                MERGE INTO position_overalls t
                USING (SELECT :card_id AS card_id, :pos AS position_name FROM dual) s
                ON (t.card_id = s.card_id AND t.position_name = s.position_name)
                WHEN NOT MATCHED THEN
                  INSERT (card_id, position_name, overall_rating)
                  VALUES (s.card_id, s.position_name, :rating)
            """, {'card_id': card_id, 'pos': pos, 'rating': rating})

        conn.commit()
    except Exception as e:
        log_failed(card_id, f"DB 저장 오류: {e}")
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

def process_card(card_id):
    try:
        site_id = fix_card_id(card_id)
        soup = fetch_position_data(site_id)
        mains = extract_main_positions(soup)
        overs = extract_position_overalls(soup)
        save_to_db(card_id, mains, overs)
    except Exception as e:
        log_failed(card_id, f"전체 실패: {e}")

if __name__ == "__main__":
    card_ids = load_card_ids()
    print(f"📝 총 {len(card_ids)}개 카드 포지션 수집 시작")

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(process_card, card_ids), total=len(card_ids), desc="진행률"))

    print("✅ 포지션 저장 완료")
