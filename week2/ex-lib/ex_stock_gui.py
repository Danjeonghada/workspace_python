from tkinter import *
from tkinter import messagebox, ttk
from week2.ex_db.DBManager import DBManager
import threading
db = DBManager()
def fetch_stock_data():
    """주식 종목명,코드,수집여부를 가져옴."""
    return db.select("SELECT krx_code, krx_name, krx_yn FROM tb_krx")
def update_collect_yn(code, flag):
    """선택한 주식의 수집 여부를 업데이트"""
    db.insert("UPDATE tb_krx SET krx_yn=:1 WHERE krx_code=:2"
             ,[flag, code])
def update_selected(event):
    """선택시 화면 표시"""
    selected_stock = stock_combobox.get()
    for stock in stock_list:
        if f"{stock[0]} - {stock[1]}" == selected_stock:
            collect_var.set(stock[2])
            break
def on_save():
    """선택 정보 저장"""
    selected_stock = stock_combobox.get()
    new_flag = collect_var.get()
    if not selected_stock:
        messagebox.showwarning("Warning", "종목을 선택하세요!")
        return
    stock_code = selected_stock.split(" - ")[0]
    update_collect_yn(stock_code, new_flag)
    messagebox.showwarning("success", "데이터 저장됨.")
    # 갱신
    load_data()
def load_data():
    """스레드를 사용하여 데이터를 비동기적으로 로드"""
    def task():
        global stock_list
        stock_list = fetch_stock_data()
        new_values = [f"{s[0]} - {s[1]}" for s in stock_list]
        # UI 업데이트 (메인 스레드에서 실행해야 함)
        app.after(0, update_combobox, new_values)
    thread = threading.Thread(target=task, daemon=True)
    thread.start()

def update_combobox(new_values):
    """Combobox를 새 데이터로 갱신하며 선택값 유지"""
    current_selection = stock_combobox.get()  # 현재 선택된 값 저장
    stock_combobox['values'] = new_values  # 새로운 값 설정
    stock_combobox.set("")  # 선택값 초기화
    # 기존 값이 있으면 다시 설정
    if current_selection in new_values:
        stock_combobox.set(current_selection)

app = Tk()
app.title("stock bbs manager")
app.geometry("400x200")
# 종목 Combobox
stock_list = []
stock_combobox = ttk.Combobox(app, state="readonly", width=30)
stock_combobox.grid(row=0, column=1, padx=10, pady=10)
stock_combobox.bind("<<ComboboxSelected>>", update_selected)
# 수집 여부 선택
collect_var = StringVar(value="N")
yes_btn = ttk.Radiobutton(app, text="Yes", variable=collect_var, value="Y")
no_btn = ttk.Radiobutton(app, text="No", variable=collect_var, value="N")
yes_btn.grid(row=1, column=1, padx=10, pady=5, sticky="w")
no_btn.grid(row=1,column=1, padx=10, pady=5, sticky="e")
# 저장 버튼
save_btn = ttk.Button(app, text="Save", command=on_save)
save_btn.grid(row=2, column=1, pady=10)
# 데이터 로드(스레드 사용)
load_data()
app.mainloop()
