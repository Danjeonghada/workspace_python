import cx_Oracle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'

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

for card_id in card_ids:
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

        # 생일 추출
        birth_tag = soup.select_one("span.etc.birth")
        birth_str = birth_tag.text.strip() if birth_tag else None
        birth_date = None
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y.%m.%d")
            except ValueError:
                print(f"❌ 생일 파싱 실패: {birth_str}")

        # 국가 추출
        nation_tag = soup.select_one("div.nation span.txt")
        nation_name = nation_tag.text.strip() if nation_tag else None
        nation_id = None
        if nation_name:
            cursor.execute("SELECT nation_id FROM nations WHERE nation_name = :1", [nation_name])
            result = cursor.fetchone()
            if result:
                nation_id = result[0]
            else:
                print(f"⚠ 국가 없음: {nation_name}")

        # players 테이블 생존 여부 확인 후 UPDATE만 수행
        cursor.execute("SELECT 1 FROM players WHERE player_id = :1", [player_id])
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
                UPDATE players
                SET birth_date = :birth_date,
                    nation_id = :nation_id
                WHERE player_id = :player_id
            """, {
                'player_id': player_id,
                'birth_date': birth_date,
                'nation_id': nation_id
            })
            print(f"✔ 업데이트됨: player_id={player_id}, birth={birth_date}, nation={nation_name} → id={nation_id}")
        else:
            print(f"⚠ player_id={player_id} 없음 → 생략")

    except Exception as e:
        print(f"❌ 예외 발생(card_id={card_id}): {e}")
        continue

conn.commit()
cursor.close()
conn.close()
driver.quit()
print("✅ 전체 players 테이블 업데이트 완료")