import cx_Oracle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

# 스레드 로컬 저장소
thread_local = threading.local()
print_lock = threading.Lock()  # 출력 동기화용


def get_driver():
    """각 스레드마다 독립적인 웹 드라이버 인스턴스 생성"""
    if not hasattr(thread_local, "driver"):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        thread_local.driver = webdriver.Chrome(options=options)
    return thread_local.driver


def get_connection():
    """각 스레드마다 독립적인 데이터베이스 연결"""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = cx_Oracle.connect(username, password, dsn)
    return thread_local.conn


def safe_print(*args, **kwargs):
    """출력 동기화"""
    with print_lock:
        print(*args, **kwargs)


def process_card(card_id):
    """각 카드에 대한 데이터를 추출하고 DB 업데이트"""
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
            safe_print(f"⚠ 알림창 닫힘: {alert.text}")
            alert.dismiss()
            return
        except TimeoutException:
            pass

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ovr_set'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 데이터 추출
        overall = soup.select_one("div.ovr.value").text.strip() if soup.select_one("div.ovr.value") else None
        height = soup.select_one("span.etc.height").text.strip() if soup.select_one("span.etc.height") else None
        weight = soup.select_one("span.etc.weight").text.strip() if soup.select_one("span.etc.weight") else None
        body_type = soup.select_one("span.etc.physical").text.strip() if soup.select_one("span.etc.physical") else None
        skill_moves = soup.select_one("span.etc.skill").text.strip() if soup.select_one("span.etc.skill") else None
        main_position = soup.select_one("div.position").text.strip() if soup.select_one("div.position") else None
        salary = soup.select_one("div.pay span").text.strip() if soup.select_one("div.pay span") else None
        foot = soup.select_one("span.etc.foot strong").text.strip() if soup.select_one("span.etc.foot strong") else None

        # 왼발, 오른발 추출
        left_foot = None
        right_foot = None
        if "L" in soup.select_one("span.etc.foot").text:
            left_foot = soup.select_one("span.etc.foot").text.split("L")[1].strip() if "L" in soup.select_one(
                "span.etc.foot").text else None
        if "R" in soup.select_one("span.etc.foot").text:
            right_foot = soup.select_one("span.etc.foot").text.split("R")[1].strip() if "R" in soup.select_one(
                "span.etc.foot").text else None

        # player_cards 테이블에 데이터 삽입
        cursor.execute("""
            UPDATE player_cards
            SET overall = :overall, height = :height, weight = :weight, body_type = :body_type,
                skill_moves = :skill_moves, main_position = :main_position, salary = :salary,
                foot = :foot, left_foot = :left_foot, right_foot = :right_foot
            WHERE card_id = :card_id
        """, {
            'overall': overall,
            'height': height,
            'weight': weight,
            'body_type': body_type,
            'skill_moves': skill_moves,
            'main_position': main_position,
            'salary': salary,
            'foot': foot,
            'left_foot': left_foot,
            'right_foot': right_foot,
            'card_id': card_id
        })
        conn.commit()
        safe_print(f"✔ 업데이트됨: card_id={card_id}, overall={overall}, salary={salary}, position={main_position}")

    except Exception as e:
        safe_print(f"❌ 예외 발생(card_id={card_id}): {e}")
    finally:
        cursor.close()


def cleanup():
    """최종 정리: 연결 및 드라이버 종료"""
    if hasattr(thread_local, "conn"):
        thread_local.conn.close()
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()


if __name__ == '__main__':
    # 카드 ID 목록 가져오기
    conn = cx_Oracle.connect(username, password, dsn)
    cursor = conn.cursor()
    cursor.execute("SELECT card_id FROM player_cards")
    card_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # 진행률 바와 함께 병렬 실행
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(tqdm(executor.map(process_card, card_ids), total=len(card_ids), desc="진행률"))

    cleanup()
    safe_print("✅ 전체 업데이트 완료")
