from tkinter import *
from tkinter import filedialog, messagebox
# pdf 생성s
# pip install reportlab
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    messagebox.showinfo("라이브러리 에러ㅠ_ㅠ", "reportlab 설치되어 있지 않습니다.")

def export_as_pdf():
    """ Text 위젯의 내용을 PDF 파일로 내보냅니다 (ReportLab 사용). """
    content = text_area.get("1.0", END).rstrip()
    if not content:
        messagebox.showwarning("경고", "PDF로 내보낼 내용이 없습니다.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
    )
    if file_path:
        pdfmetrics.registerFont(TTFont('맑은고딕', "malgun.ttf"))
        # ReportLab으로 PDF 생성
        c = canvas.Canvas(file_path, pagesize=A4)
        c.setFont("맑은고딕", 16)
        width, height = A4

        # PDF에 작성할 시작 위치 (왼쪽 여백, 상단 여백)
        x_margin = 50
        y_position = height - 50
        line_spacing = 15

        lines = content.split("\n")
        for line in lines:
            # 한 줄 출력
            c.drawString(x_margin, y_position, line)
            y_position -= line_spacing
            # 페이지 바닥에 닿으면 새로운 페이지로 넘어가기
            if y_position < 50:
                c.showPage()
                y_position = height - 50

        c.save()
        messagebox.showinfo("PDF 내보내기", f"PDF 파일이 '{file_path}'에 저장되었습니다.")
def new_file():
    """새 파일 생성"""
    # 텍스트 위젯의 내용을 모두 지우고, 파일 경로 변수도 초기화. (새 파일)
    global current_file
    current_file = None
    text_area.delete('1.0', END)
    app.title("메모장 - 새 파일")

def open_file():
    """기존의 txt 파일 열기"""
    global current_file # 전역 변수 사용
    file_path = filedialog.askopenfilename(
        filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )
    if file_path:
        current_file = file_path
        f = open(file_path, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        text_area.delete("1.0", END)
        text_area.insert("1.0", content)
        app.title(f"메모장 - {current_file}")

def save_file_as():
    """다른 이름으로 저장하기"""
    global current_file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )
    if file_path:
        current_file = file_path
        # 파일 or db 와 같은 연결 사용 시 with -> close를 자동으로 해줌
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_area.get('1.0', END))
        messagebox.showinfo("저장 완료", f"'{current_file}'에 저장됨.")
        app.title(f"메모장 - {current_file}")

def save_file(event=None):
    """열려있는 파일에 덮어쓰기"""
    global current_file
    if current_file is None:
        # 한 번도 저장한 적이 없다면 -> 다른 이름으로 저장 호출
        save_file_as()
    else:
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write(text_area.get('1.0', END))
        messagebox.showinfo("저장 완료", f"'{current_file}'에 저장됨.")

def exit_app():
    """프로그램 종료"""
    app.destroy()

app = Tk()
app.title("메모장")
current_file = None

text_area = Text(app)
text_area.pack(expand=True, fill='both')
# 메뉴바 생성
menubar = Menu(app)
# '파일' 메뉴 생성
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label='새로 만들기', command=new_file)
file_menu.add_command(label='열기', command=open_file)
file_menu.add_command(label='다른 이름으로 저장', command=save_file_as)
file_menu.add_command(label='저장', command=save_file)
# 하위 메뉴
sub_menu = Menu(file_menu, tearoff=0)
sub_menu.add_command(label='PDF로 저장', command=export_as_pdf)
sub_menu.add_command(label='TXT로 저장')
file_menu.add_cascade(label='내보내기', menu=sub_menu)
file_menu.add_separator() # 구분선
file_menu.add_command(label='종료', command=exit_app)
# 파일 메뉴를 메뉴바에
menubar.add_cascade(label='파일', menu=file_menu)
# 메뉴바를 연결
app.config(menu=menubar)
app.bind('<Control-s>', save_file)
app.mainloop()