from tkinter import *
app = Tk()
def fn_click(event):
    print(f"마우스 클릭 위치 :{event.x}, {event.y}")

def fn_push(event):
    print(f"키보드 입력 :{event.char}")

frame = Frame(app, width=300, height=300)
# 왼쪽 마우스
frame.bind("<Button-1>", fn_click)
# 키보드
frame.bind('<Key>', fn_push)
frame.focus_set()
frame.pack()
frame.mainloop()