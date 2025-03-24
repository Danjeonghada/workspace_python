from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
url = 'https://sports.news.naver.com/kfootball/record/index'
driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get(url)
time.sleep(1)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()
tbody = soup.find('tbody')
print(tbody)
trs = tbody.find_all('tr')
for team in trs:
    rank = team.find('th').strong.text.strip()
    team_name = team.find('td', class_='tm').find_all('span')[1].text.strip()
    print(f"순위: {rank}, 구단명: {team_name}")