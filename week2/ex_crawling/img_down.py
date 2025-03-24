import urllib.request as req

url = 'https://img.cgv.co.kr/Movie/Thumbnail/Poster/000089/89304/89304_320.jpg'
req.urlretrieve(url, 'text.png')