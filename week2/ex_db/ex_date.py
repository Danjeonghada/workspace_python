import datetime
now = datetime.datetime.now()
print("현재 날짜와 시간", now)
# format to string
format_now = now.strftime("%Y-%m-%d %H:%M:%S")
print(format_now)
format_now2 = now.strftime("%y-%m-%d %H %M %S")
print(format_now2) # 대소문자 표현이 다름
time_now = now.timestamp()
print(time_now)
time_to_date = datetime.datetime.fromtimestamp(time_now).strftime("%Y-%m-%d")
print(time_to_date)
# 문자열 to 데이트 타임
date_str = "2025- 01-17 09:10:00"
start_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")