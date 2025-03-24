from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("chromedriver")  # 크롬 드라이버 경로 지정 (경로에 맞게 변경)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://fconline.nexon.com/datacenter"
driver.get(url)

time.sleep(3)  # 페이지 로딩 대기 (필요에 따라 조절)

seasons = driver.find_elements(By.CLASS_NAME, "season")

for season in seasons:
    print(season.text.strip())

driver.quit()
