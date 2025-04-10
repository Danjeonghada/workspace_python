import requests
import cx_Oracle
import threading
from queue import Queue
from tqdm import tqdm
import logging
import json

# 설정
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'
MINIFACE_URL = "https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{}.png"
FACEON_URL = "https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/players/p{}.png"
NUM_THREADS = 4

# 로깅
logging.basicConfig(filename='image_url_insert.log', level=logging.INFO)

# 멀티스레드 제어용
task_queue = Queue()
pbar_lock = threading.Lock()
fail_list_lock = threading.Lock()
failed_cards = []

# DB 연결
def db_connection():
    return cx_Oracle.connect(username, password, dsn)

# 워커 스레드
def worker(pbar):
    conn = db_connection()
    cursor = conn.cursor()
    count = 0

    while True:
        item = task_queue.get()
        if item is None:
            break

        card_id, player_id = item

        try:
            update_needed = False

            miniface_url = MINIFACE_URL.format(card_id)
            faceon_url = FACEON_URL.format(player_id)

            if requests.head(miniface_url, timeout=3).status_code == 200:
                cursor.execute("""
                    MERGE INTO player_cards pc
                    USING (SELECT :1 AS card_id, :2 AS miniface_url FROM dual) d
                    ON (pc.card_id = d.card_id)
                    WHEN MATCHED THEN
                      UPDATE SET pc.miniface_url = d.miniface_url
                      WHERE pc.miniface_url IS NULL
                """, (card_id, miniface_url))
                update_needed = True

            if requests.head(faceon_url, timeout=3).status_code == 200:
                cursor.execute("""
                    MERGE INTO players p
                    USING (SELECT :1 AS player_id, :2 AS faceon_url FROM dual) d
                    ON (p.player_id = d.player_id)
                    WHEN MATCHED THEN
                      UPDATE SET p.faceon_url = d.faceon_url
                      WHERE p.faceon_url IS NULL
                """, (player_id, faceon_url))
                update_needed = True

            if update_needed:
                count += 1
                if count >= 20:
                    conn.commit()
                    count = 0

        except Exception as e:
            logging.error(f"[ERROR] card_id={card_id}, player_id={player_id} → {e}")
            with fail_list_lock:
                failed_cards.append({"card_id": card_id, "player_id": player_id})

        with pbar_lock:
            pbar.update(1)

        task_queue.task_done()

    conn.commit()
    cursor.close()
    conn.close()

# 데이터 로딩
def get_card_data():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT card_id, player_id FROM player_cards")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# 메인 실행
def main():
    data = get_card_data()
    for item in data:
        task_queue.put(item)

    with tqdm(total=len(data), miniters=1, mininterval=0, desc="진행 중", unit="건") as pbar:
        threads = []
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=worker, args=(pbar,))
            t.start()
            threads.append(t)

        task_queue.join()

        for _ in range(NUM_THREADS):
            task_queue.put(None)
        for t in threads:
            t.join()

    # 실패 카드 JSON 저장
    if failed_cards:
        with open("failed_cards.json", "w", encoding="utf-8") as f:
            json.dump(failed_cards, f, ensure_ascii=False, indent=2)
        print(f"⚠️ 실패한 카드 {len(failed_cards)}건 저장됨: failed_cards.json")

    print("✅ 병렬 + MERGE + 실패 저장 완료!")

if __name__ == "__main__":
    main()
