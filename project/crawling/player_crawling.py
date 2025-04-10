import cx_Oracle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import threading

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 스레드 로컬 저장소 및 락
thread_local = threading.local()
print_lock = threading.Lock()
log_lock = threading.Lock()

# 안전한 로그 출력 (print로 복원)
def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# 에러 로그 파일 저장
def log_error(message):
    with log_lock:
        with open("../position_code.txt", "a", encoding="utf-8") as f:
            f.write(message + "\n")

def get_driver():
    if not hasattr(thread_local, "driver"):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        thread_local.driver = webdriver.Chrome(options=options)
    return thread_local.driver

def get_connection():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn

def process_card(card_id):
    driver = get_driver()
    conn = get_connection()
    cursor = conn.cursor()

    player_id = card_id % 1_000_000
    url = f"https://fconline.nexon.com/DataCenter/PlayerInfo?spid={card_id}&n1Strong=1"

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            msg = f"⚠ 알림창 닫힘: {alert.text}"
            safe_print(msg)
            log_error(msg)
            alert.dismiss()
            return
        except TimeoutException:
            pass

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ovr_set'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 생일
        birth_tag = soup.select_one("span.etc.birth")
        birth_str = birth_tag.text.strip() if birth_tag else None
        birth_date = None
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y.%m.%d")
            except ValueError:
                msg = f"❌ 생일 파싱 실패: {birth_str}"
                safe_print(msg)
                log_error(msg)

        # 국가
        nation_tag = soup.select_one("div.nation span.txt")
        nation_name = nation_tag.text.strip() if nation_tag else None
        nation_id = None
        national_player = 'N'
        if nation_name:
            if '국가대표' in nation_name:
                national_player = 'Y'
            nation_name_clean = nation_name.split(',')[0].strip()
            cursor.execute("SELECT nation_id FROM nations WHERE nation_name = :1", [nation_name_clean])
            result = cursor.fetchone()
            if result:
                nation_id = result[0]
            else:
                safe_print(f"⚠ 국가 없음: '{nation_name_clean}' (원본: '{nation_name}')")

        # 클럽
        club_tag = soup.select_one("div.etc.team span.txt")
        club_name = club_tag.text.strip() if club_tag else None
        club_id = None
        if club_name:
            cursor.execute("SELECT club_id FROM clubs WHERE club_name = :1", [club_name.strip()])
            result = cursor.fetchone()
            if result:
                club_id = result[0]
            else:
                safe_print(f"⚠ 클럽 없음: {club_name}")

        # UPDATE
        cursor.execute("SELECT 1 FROM players WHERE player_id = :1", [player_id])
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
                UPDATE players
                SET birth_date = :birth_date,
                    nation_id = :nation_id,
                    national_player = :national_player,
                    club_id = :club_id
                WHERE player_id = :player_id
            """, {
                'player_id': player_id,
                'birth_date': birth_date,
                'nation_id': nation_id,
                'national_player': national_player,
                'club_id': club_id
            })
            conn.commit()
            safe_print(f"✔ 업데이트됨: player_id={player_id}, birth={birth_date}, nation={nation_name_clean} → id={nation_id}, club={club_name}")
        else:
            safe_print(f"⚠ player_id={player_id} 없음 → 생략")

    except Exception as e:
        msg = f"❌ 예외 발생(card_id={card_id}): {e}"
        safe_print(msg)
        log_error(msg)

    finally:
        cursor.close()

def cleanup():
    try:
        if hasattr(thread_local, "driver"):
            thread_local.driver.quit()
    except Exception as e:
        msg = f"⚠ 드라이버 종료 중 예외 발생: {e}"
        safe_print(msg)
        log_error(msg)

    try:
        if hasattr(thread_local, "conn"):
            thread_local.conn.close()
    except Exception as e:
        msg = f"⚠ DB 연결 종료 중 예외 발생: {e}"
        safe_print(msg)
        log_error(msg)

if __name__ == '__main__':
    conn = cx_Oracle.connect(username, password, dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM player_cards")
    card_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(process_card, card_ids), total=len(card_ids), desc="진행률"))

    cleanup()
    print("✅ 전체 업데이트 완료")
