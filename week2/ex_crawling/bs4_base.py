# pip install bs4
from bs4 import BeautifulSoup
import requests

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie&quot; class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie&quot; class="sister" id="link2" /> and
<a href="http://example.com/tillie&quot; class="sister">Tillie</a>
<a href="http://example.com/tillie&quot; class="sister">한글</a>
and they lived at the bottom of a well.</p>
<p class="story">...</p>
</body>
</html>
"""
soup = BeautifulSoup(html_doc, 'html.parser')
print(soup.prettify()) # 구조화 되게 출력
a_all = soup.find_all('a', string=True) # text가 있는 a 태그만
for a in a_all:
    # print(a)
    print(a['href'])
    print(a.text)

import re
# re 정규표현식 라이브러리
text_l = soup.find_all('a', string=re.compile('l')) # 텍스트에 l이 존재하는
text_han = soup.find('a', string=re.compile('[가-힣]')) # 한글이 존재하는
print(text_l)
print(text_han)

# select 다건
# select_one
link1 = soup.select_one("#link1") # # id
cls = soup.select('.sister')      # . class
print(link1)
print(cls)