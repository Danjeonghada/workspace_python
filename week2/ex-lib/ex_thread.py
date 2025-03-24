import threading
import time

def task(nm, delay):
    print(f"{nm} 스레드 시작!")
    time.sleep(delay)
    print(f"{nm} 스레드 종료")

# 스레드 생성
t1 = threading.Thread(target=task, args=("job1", 2))
t2 = threading.Thread(target=task, args=("job2", 3))

# 스레드 실행
t1.start()
t2.start()

# 스레드 종료될 때 까지 대기
t1.join()
t2.join()
print()
print("main 종료")