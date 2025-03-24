from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

url = "https://www.hanatour.com/package/international"
# 백그라운드 실행 옵션 추가
option = webdriver.ChromeOptions()
option.add_argument('--headless')
driver = webdriver.Chrome(options=option)
driver.implicitly_wait(3)
driver.get(url)
time.sleep(1)
input_search = driver.find_element(By.ID, 'input_keyword')
# input에 value 적용
input_search.send_keys("하와이")
# button click
driver.find_element(By.CSS_SELECTOR, 'button.btn_search').click()
time.sleep(1)
# 탭 클릭
driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/ul/li[2]/a').click()
time.sleep(1)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()
lis = soup.select_one('.prod_list li')
for li in lis:
    try:
        print(li.select_one('.txt_info .tit').text)
    except Exception as e:
        print(str(e))