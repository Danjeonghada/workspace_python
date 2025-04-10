from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import cx_Oracle

# Oracle 연결 정보
username = 'dan'
password = 'dan'
dsn = 'localhost:1521/xe'


# 스레드 로컬 저장소
def get_connection():
    """데이터베이스 연결 생성"""
    return cx_Oracle.connect(username, password, dsn)


def get_driver():
    """웹 드라이버 설정"""
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver


def safe_print(*args, **kwargs):
    """출력 동기화"""
    print(*args, **kwargs)


def process_trait():
    """특성 데이터 추출 및 데이터베이스에 저장"""
    driver = get_driver()
    conn = get_connection()
    cursor = conn.cursor()

    url = "https://namu.wiki/w/FC%20%EC%98%A8%EB%9D%BC%EC%9D%B8/%ED%8A%B9%EC%84%B1"
    driver.get(url)

    # JavaScript로 로드된 데이터를 기다리기 (특정 요소가 로드될 때까지)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-v-f564c30b]'))
        )

        # trait 데이터 추출
        trait_elements = driver.find_elements(By.CSS_SELECTOR, 'strong[data-v-f564c30b]')

        for element in trait_elements:
            trait_info = element.text.strip()
            if ':' in trait_info:
                trait_name, trait_description = trait_info.split(":", 1)
                trait_name = trait_name.strip()
                trait_description = trait_description.strip()

                # 시퀀스를 사용하여 TRAIT_ID 자동 생성
                cursor.execute("""
                    INSERT INTO trait_master (TRAIT_ID, TRAIT_NAME, TRAIT_INFO)
                    VALUES (seq_trait_id.NEXTVAL, :trait_name, :trait_description)
                """, {
                    'trait_name': trait_name,
                    'trait_description': trait_description
                })

                conn.commit()
                safe_print(f"✔ 저장됨: {trait_name} - {trait_description}")

    except Exception as e:
        safe_print(f"❌ 데이터 추출 중 오류: {e}")
    finally:
        cursor.close()
        conn.close()
        driver.quit()


if __name__ == '__main__':
    process_trait()
    safe_print("✅ 데이터 추출 및 저장 완료")
