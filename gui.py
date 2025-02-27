# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 00:24:47 2025

@author: replica
"""
import chzzk_review_segment_downloader as crsd
import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import webbrowser
import winsound

RED = "#a31f5f"
GREEN = "#1fa372"

def on_button_click():
    def task():
        button.configure(state="disabled")
        status_label.configure(text_color=RED)
        url = entry.get()
        CSE.NID_AUT, CSE.NID_SES = get_NID()
        
        download_path = path_entry.get()
        
        start_time_str = start_entry.get()
        end_time_str = end_entry.get()
        start_time = crsd.convert_time_to_seconds(start_time_str, add_log)
        end_time = crsd.convert_time_to_seconds(end_time_str, add_log)
        if url and start_time is not None and end_time is not None:
            CSE.extract_streams(url, start_time, end_time, start_time_str, end_time_str, download_path)
        else:
            add_log("Please provide valid inputs")
        button.configure(state="normal")
        status_label.configure(text_color=GREEN)
        download_complete_popup()
        progress_update(0)
        speed_update(0)

    thread = threading.Thread(target=task)
    thread.start()
    
def save_download_path(path: str):
    with open("config", "w") as f:
        f.write(path)

def load_download_path():
    with open("config", "r") as f:
        path = f.read()
        if not path == "":
            path_entry.insert(0, path)
            
def select_download_path():
    init_path = path_entry.get()
    if init_path == "":
        init_path = os.getcwd()
        
    path = filedialog.askdirectory(title = "다운로드 폴더 선택창", initialdir = init_path)
    if path:
        path_entry.delete(0, "end")
        path_entry.insert(0, path)
        save_download_path(path)

def open_download_path():
    path = path_entry.get()
    if path == "":
        path = os.getcwd()
    
    if os.path.isdir(path):
        os.startfile(path)

def open_github():
    github_url = "https://github.com/junobonnie/chzzk_review_segment_downloader"  # 이동할 GitHub 페이지 URL
    webbrowser.open(github_url)  # 기본 브라우저로 URL 열기

def get_NID():
    with open("NID.txt", "r") as f:
        NID = f.read().split(" ")
    if not len(NID) == 2:
        NID = ["", ""]
    return NID

def get_popup_pos(popup_width, popup_height):
    root_x = root.winfo_x()  # 메인 창의 X 좌표
    root_y = root.winfo_y()  # 메인 창의 Y 좌표
    root_width = root.winfo_width()  # 메인 창의 너비
    root_height = root.winfo_height()  # 메인 창의 높이

    # 팝업 창 위치 계산 (메인 창 중심)
    popup_x = root_x + (root_width // 2) - (popup_width // 2)
    popup_y = root_y + (root_height // 2) - (popup_height // 2)
    return popup_x, popup_y

# 팝업창 생성 함수
def open_popup():
    # 팝업 창 생성
    popup_width, popup_height = 250, 150
    popup_x, popup_y = get_popup_pos(popup_width, popup_height)
    
    popup = ctk.CTkToplevel(root)
    popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        
    popup.title("NID 수정")
    popup.grab_set()  # 모달 창으로 설정 (메인 창 비활성화)

    NID_AUT, NID_SES = get_NID()

    # 라벨과 입력창을 같은 행에 배치
    input_area = ctk.CTkFrame(popup, width=250, corner_radius=0)
    input_area.pack()
    
    label_prompt1 = ctk.CTkLabel(input_area, text="NID_AUT")
    label_prompt1.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # 좌측 정렬
    
    entry1 = ctk.CTkEntry(input_area, width=150, placeholder_text=NID_AUT)
    entry1.grid(row=0, column=1, padx=10, pady=10)
    
    label_prompt2 = ctk.CTkLabel(input_area, text="NID_SES")
    label_prompt2.grid(row=1, column=0, padx=10, pady=10, sticky="w")  # 좌측 정렬
    
    entry2 = ctk.CTkEntry(input_area, width=150, placeholder_text=NID_SES)
    entry2.grid(row=1, column=1, padx=10, pady=10)
    
    def save_NID():
        NID_AUT = entry1.get()  # 입력 필드의 텍스트 가져오기
        NID_SES = entry2.get()
        
        if not (NID_AUT == "" and NID_SES == ""):
            with open("NID.txt", "w") as f:
                f.write(NID_AUT+" "+NID_SES)
                
            popup_width, popup_height = 100, 50
            popup_x, popup_y = get_popup_pos(popup_width, popup_height)
            
            new_popup = ctk.CTkToplevel(root)
            new_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
            new_popup.title("")
            new_popup.grab_set()
            label = ctk.CTkLabel(new_popup, text="저장완료")
            label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        
    button0 = ctk.CTkButton(popup, text="저장하기", command=save_NID)
    button0.pack(padx=10, pady=10)
    
def download_complete_popup():
    popup_width, popup_height = 100, 50
    popup_x, popup_y = get_popup_pos(popup_width, popup_height)
    
    new_popup = ctk.CTkToplevel(root)
    new_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
    new_popup.title("")
    new_popup.grab_set()
    label = ctk.CTkLabel(new_popup, text="다운로드 완료")
    label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
    winsound.MessageBeep()
    
# 새로운 텍스트 추가 함수
def add_log(text):
    scrollable_log.configure(state="normal")  # 편집 가능하게 설정
    scrollable_log.insert("end", "\n\n%s"%(text))  # 새로운 텍스트 추가
    scrollable_log.configure(state="disabled")  # 다시 편집 불가능하게 설정
    scrollable_log.yview_moveto(1.0)  # 스크롤을 가장 아래로 이동

def progress_update(value):
    progress_bar.set(value/100)
    download_percent_label.configure(text="%.2f%%"%(value))
    
def speed_update(value):
    if value < 1000:
        download_speed_label.configure(text_color=RED)
    else:
        download_speed_label.configure(text_color=GREEN)
    download_speed_label.configure(text="%.2f kB/s"%(value))
    
CSE = crsd.ChzzkStreamExtractor(add_log, progress_update, speed_update)

# UI 초기화
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("치지직 다시보기 구간 다운로더")
root.geometry("500x230")
root.iconbitmap("icon.ico")

# 좌측 메뉴바 생성
menu_bar = ctk.CTkFrame(root, width=100, corner_radius=0)
menu_bar.pack(side="left", fill="y")

info_button = ctk.CTkButton(menu_bar, text="프로그램 정보", width=100, command=open_github)
info_button.pack(pady=10, padx=10, fill="x")

NID_button = ctk.CTkButton(menu_bar, text="NID 수정", width=100, command=open_popup)
NID_button.pack(pady=0, padx=10, fill="x")

# 스크롤 가능한 로그
scrollable_log = ctk.CTkTextbox(menu_bar, width=100, wrap="word")
scrollable_log.insert("1.0", "Hello!")
scrollable_log.configure(state="disabled")  # 편집 불가능하게 설정
scrollable_log.pack(pady=10)

# URL 입력 필드
entry = ctk.CTkEntry(root, placeholder_text="다시보기 방송주소를 입력하세요")
entry.pack(pady=10, padx=25, fill='x')

# 시간 입력 필드
time_frame = ctk.CTkFrame(root, fg_color="transparent")
time_frame.pack(pady=10, padx=20, fill='x')

start_entry = ctk.CTkEntry(time_frame, placeholder_text="00:00:00", width=50)
start_entry.pack(side="left", fill='x', expand=True, padx=5)

# 라벨 생성
label = ctk.CTkLabel(time_frame, text="~")
label.pack(side="left", padx=5)

end_entry = ctk.CTkEntry(time_frame, placeholder_text="00:00:00", width=50)
end_entry.pack(side="right", fill='x', expand=True, padx=5)

# 다운로드 경로 입력 필드 및 버튼
path_frame = ctk.CTkFrame(root, fg_color="transparent")
path_frame.pack(pady=10, padx=20, fill='x')

path_entry = ctk.CTkEntry(path_frame, placeholder_text="다운로드 경로를 선택하세요", width=200)
path_entry.pack(side="left", fill='x', expand=True, padx=5)

load_download_path()

path_button = ctk.CTkButton(path_frame, text="찾기", command=select_download_path, width=20)
path_button.pack(side="left", padx=5)

open_button = ctk.CTkButton(path_frame, text="열기", command=open_download_path, width=20)
open_button.pack(side="right", padx=5)

# 다운로드 버튼
download_frame = ctk.CTkFrame(root, fg_color="transparent")
download_frame.pack(pady=10, padx=20, fill='x')

# 진행 상태 바
progress_bar = ctk.CTkProgressBar(download_frame)
progress_bar.pack(side="left", fill='x', expand=True, padx=5)
progress_bar.set(0)


status_label = ctk.CTkLabel(download_frame, text="●", text_color="#1fa372")
status_label.pack(side="left", padx=5)

# 확인 버튼 및 진행 상태 바 배치
button = ctk.CTkButton(download_frame, text="다운로드", command=on_button_click, width=90)
button.pack(side="right", padx=5)

# 다운로드 상태 표시
download_status_frame = ctk.CTkFrame(root, fg_color="transparent")
download_status_frame.pack(pady=0, padx=20, fill='x')

download_percent_label = ctk.CTkLabel(download_status_frame, text="0.0%", text_color=GREEN, width=100)
download_percent_label.pack(side="left", padx=5)

download_speed_label = ctk.CTkLabel(download_status_frame, text="0.0 kB/s", text_color=RED, width=100)
download_speed_label.pack(side="left", padx=5)

# 실행
root.mainloop()
