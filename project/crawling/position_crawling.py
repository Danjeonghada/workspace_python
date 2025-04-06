import cx_Oracle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Oracle 연결 정보
username = 'dan'
password = 'dan'
# dsn = 'localhost:1521/xe'
dsn = '192.168.219.106'

# 셀레니움 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Oracle 연결
conn = cx_Oracle.connect(username, password, dsn)
cursor = conn.cursor()

# player_cards 테이블에서 모든 card_id 가져오기
cursor.execute("SELECT card_id FROM player_cards")
card_ids = [row[0] for row in cursor.fetchall()]
total_cards = len(card_ids)  # 총 카드 수

# 커밋할 데이터를 저장할 리스트
update_data = []

for idx, card_id in enumerate(card_ids):
    player_id = str(card_id % 1_000_000)
    url = f"https://fconline.nexon.com/DataCenter/PlayerInfo?spid={card_id}&n1Strong=1"
    try:
        driver.get(url)

        # 알림창 확인
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"⚠ 알림창 닫힘: {alert.text}")
            alert.dismiss()
            continue
        except TimeoutException:
            pass

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ovr_set'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 포지션 및 오버롤 추출
        position_tag = soup.select_one("span.etc.position")
        position = position_tag.text.strip() if position_tag else None

        ovr_tag = soup.select_one("span.etc.ovr")
        ovr = ovr_tag.text.strip() if ovr_tag else None

        # 선수의 포지션 및 오버롤이 있다면 DB 업데이트
        if position and ovr:
            update_data.append((card_id, position, int(ovr)))  # 오버롤을 정수형으로 변환
            print(f"✔ 업데이트됨: card_id={card_id}, position={position}, ovr={ovr}")

        # 10개마다 진행률 출력
        if (idx + 1) % 10 == 0:
            progress = (idx + 1) / total_cards * 100
            print(f"⏳ 진행률: {progress:.2f}% ({idx + 1}/{total_cards})")

        # 100개씩 커밋
        if len(update_data) >= 100:
            cursor.executemany("""
                INSERT INTO POSITION_OVERALLS (CARD_ID, POSITION_NAME, OVERALL_RATING)
                VALUES (:1, :2, :3)
            """, update_data)
            conn.commit()
            print("✔ 100개 데이터 커밋됨.")
            update_data.clear()  # 커밋 후 리스트 비우기

    except Exception as e:
        print(f"❌ 예외 발생(card_id={card_id}): {e}")
        continue

# 남은 데이터 커밋
if update_data:
    cursor.executemany("""
        INSERT INTO POSITION_OVERALLS (CARD_ID, POSITION_NAME, OVERALL_RATING)
        VALUES (:1, :2, :3)
    """, update_data)
    conn.commit()
    print("✔ 남은 데이터 커밋됨.")

conn.commit()
cursor.close()
conn.close()
driver.quit()
print("✅ 전체 POSITION_OVERALLS 테이블 업데이트 완료")
