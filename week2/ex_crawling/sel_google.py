from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.request as req
import os

query = '고래상어'
url = f"https://www.google.com/search?q={query}"
driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get(url)
input("해결한 후 Enter....")
driver.find_element(By.XPATH,'//*[@id="hdtb-sc"]/div/div/div[1]/div/div[2]/a/div').click()
time.sleep(1)
# 페이지 가장 하단
scroll_h = driver.execute_script('return document.body.scrollHeight')
while True:
    # 가장 하단으로 이동
    driver.execute_script(f"window.scrollTo(0, {scroll_h})")
    time.sleep(2)
    new_h = driver.execute_script("return document.body.scrollHeight")
    if scroll_h == new_h:
        print("끝까지 읽음")
        break
    scroll_h = new_h
imgs = driver.find_elements(By.TAG_NAME, 'img')
img_set = set()
for v in imgs:
    if v.get_attribute('src') != None:
        img_set.add(v.get_attribute('src'))
driver.quit()
print(img_set)
# 이미지 저장
img_dir = os.path.join('./', query) # 검색명으로 폴더
if not os.path.exists(img_dir):
    os.mkdir(img_dir)
for i, v in enumerate(img_set):
    file = os.path.join(img_dir, str(i) + '.png')
    try:
        req.urlretrieve(v, file)
    except Exception as e:
        print(str(e))
print("저장 완료")