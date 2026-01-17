import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import random
import time
import os
import csv
import requests

class InstagramChecker:
    def __init__(self, master):
        self.master = master
        self.master.title("Instagram 계정 조회기 (requests)")
        self.master.geometry("900x400")

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.thread = None

        # ---------------- Control Frame ----------------
        control_frame = ttk.Frame(master)
        control_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        for i in range(4):
            control_frame.columnconfigure(i, weight=1)

        self.btn_start = ttk.Button(control_frame, text="시작", command=self.start)
        self.btn_pause = ttk.Button(control_frame, text="일시정지", command=self.pause)
        self.btn_resume = ttk.Button(control_frame, text="재개", command=self.resume)
        self.btn_stop = ttk.Button(control_frame, text="종료", command=self.stop)

        self.btn_start.grid(row=0, column=0, sticky="nsew")
        self.btn_pause.grid(row=0, column=1, sticky="nsew")
        self.btn_resume.grid(row=0, column=2, sticky="nsew")
        self.btn_stop.grid(row=0, column=3, sticky="nsew")

        # ---------------- Input Frame ----------------
        frame_input = ttk.LabelFrame(master, text="입력/파일")
        frame_setting = ttk.LabelFrame(master, text="설정")
        frame_status = ttk.LabelFrame(master, text="실행 상태")

        frame_input.grid(row=1, column=0, sticky="nsew")
        frame_setting.grid(row=1, column=1, sticky="nsew")
        frame_status.grid(row=1, column=2, sticky="nsew")

        master.columnconfigure(0, weight=0)
        master.columnconfigure(1, weight=0)
        master.columnconfigure(2, weight=0)

        # Input
        ttk.Label(frame_input, text="IDs 파일").grid(row=0, column=0, sticky="w")
        self.ids_entry = ttk.Entry(frame_input, width=25)
        self.ids_entry.grid(row=0, column=1, sticky="w")
        ttk.Button(frame_input, text="열기", command=self.open_ids).grid(row=0, column=2, sticky="w")

        ttk.Label(frame_input, text="결과 파일").grid(row=1, column=0, sticky="w")
        self.result_entry = ttk.Entry(frame_input, width=25)
        self.result_entry.grid(row=1, column=1, sticky="w")
        ttk.Button(frame_input, text="저장", command=self.save_result).grid(row=1, column=2, sticky="w")

        ttk.Label(frame_input, text="진행 파일").grid(row=2, column=0, sticky="w")
        self.progress_entry = ttk.Entry(frame_input, width=25)
        self.progress_entry.grid(row=2, column=1, sticky="w")
        ttk.Button(frame_input, text="저장", command=self.save_progress).grid(row=2, column=2, sticky="w")

        # Settings
        ttk.Label(frame_setting, text="계정 간 휴식 (초)").grid(row=0, column=0, sticky="w")

        ttk.Label(frame_setting, text="최소").grid(row=1, column=0, sticky="w")
        self.min_sleep = ttk.Entry(frame_setting, width=6)
        self.min_sleep.grid(row=1, column=1, sticky="w")

        ttk.Label(frame_setting, text="-").grid(row=1, column=2, sticky="w")

        self.max_sleep = ttk.Entry(frame_setting, width=6)
        self.max_sleep.grid(row=1, column=3, sticky="w")

        ttk.Label(frame_setting, text="정기 휴식").grid(row=2, column=0, sticky="w")
        ttk.Label(frame_setting, text="10~15개 마다").grid(row=3, column=0, sticky="w")

        self.min_count = ttk.Entry(frame_setting, width=6)
        self.min_count.grid(row=3, column=1, sticky="w")

        ttk.Label(frame_setting, text="개").grid(row=3, column=2, sticky="w")
        ttk.Label(frame_setting, text="휴식 시간(초)").grid(row=4, column=0, sticky="w")

        self.long_sleep = ttk.Entry(frame_setting, width=6)
        self.long_sleep.grid(row=4, column=1, sticky="w")

        self.random_order_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_setting, text="순서 랜덤", variable=self.random_order_var).grid(row=5, column=0, sticky="w")

        # Status
        ttk.Label(frame_status, text="진행률").grid(row=0, column=0, sticky="w")
        self.progress_label = ttk.Label(frame_status, text="0 / 0")
        self.progress_label.grid(row=0, column=1, sticky="w")

        ttk.Label(frame_status, text="현재 아이디").grid(row=1, column=0, sticky="w")
        self.current_label = ttk.Label(frame_status, text="None")
        self.current_label.grid(row=1, column=1, sticky="w")

        ttk.Label(frame_status, text="상태").grid(row=2, column=0, sticky="w")
        self.status_label = ttk.Label(frame_status, text="대기중")
        self.status_label.grid(row=2, column=1, sticky="w")

        ttk.Label(frame_status, text="메시지").grid(row=3, column=0, sticky="w")
        self.message_label = ttk.Label(frame_status, text="")
        self.message_label.grid(row=3, column=1, sticky="w")

        self.min_sleep.insert(0, "0.5")
        self.max_sleep.insert(0, "1.5")
        self.min_count.insert(0, "10")
        self.long_sleep.insert(0, "60")

    def open_ids(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.ids_entry.delete(0, tk.END)
            self.ids_entry.insert(0, path)

    def save_result(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            self.result_entry.delete(0, tk.END)
            self.result_entry.insert(0, path)

    def save_progress(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            self.progress_entry.delete(0, tk.END)
            self.progress_entry.insert(0, path)

    def start(self):
        if self.thread and self.thread.is_alive():
            messagebox.showinfo("알림", "이미 실행 중입니다.")
            return

        self.stop_event.clear()
        self.pause_event.clear()

        self.thread = threading.Thread(target=self.run_check)
        self.thread.start()

    def pause(self):
        self.pause_event.set()
        self.status_label.config(text="일시정지")

    def resume(self):
        self.pause_event.clear()
        self.status_label.config(text="재개")

    def stop(self):
        self.stop_event.set()
        self.status_label.config(text="중단")

    def check_instagram(self, username):
        url = f"https://www.instagram.com/{username}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            res = requests.get(url, headers=headers, timeout=10)
            html = res.text

            # 삭제/비활성화 (영문/한글)
            if "Sorry, this page isn't available." in html or "Profile을(를) 이용할 수 없습니다" in html:
                return "삭제/비활성화"

            # 로그인/차단 페이지로 넘어갈 경우
            if "login" in res.url:
                return "확인불가(로그인 필요)"

            # 비공개 (영문/한글)
            if "This Account is Private" in html or "비공개 계정입니다" in html:
                return "비공개"

            # 그 외는 공개
            return "공개"

        except Exception as e:
            return f"오류: {e}"

    def run_check(self):
        ids_path = self.ids_entry.get().strip()
        result_path = self.result_entry.get().strip()
        progress_path = self.progress_entry.get().strip()

        if not ids_path or not result_path:
            messagebox.showerror("오류", "IDs 파일과 결과 파일을 먼저 설정해주세요.")
            return

        with open(ids_path, "r", encoding="utf-8") as f:
            ids = [line.strip() for line in f if line.strip()]

        start_index = 0
        if progress_path and os.path.exists(progress_path):
            with open(progress_path, "r", encoding="utf-8") as f:
                try:
                    start_index = int(f.read().strip())
                except:
                    start_index = 0

        if self.random_order_var.get():
            random.shuffle(ids)

        total = len(ids)
        self.progress_label.config(text=f"{start_index} / {total}")

        results = []

        min_sleep = float(self.min_sleep.get())
        max_sleep = float(self.max_sleep.get())
        min_count = int(self.min_count.get())
        max_count = int(self.min_count.get())
        long_sleep = float(self.long_sleep.get())

        next_long_break = random.randint(min_count, max_count)
        count_since_long_break = 0

        for idx in range(start_index, total):
            if self.stop_event.is_set():
                break

            while self.pause_event.is_set():
                time.sleep(0.1)

            username = ids[idx]
            self.current_label.config(text=username)
            self.status_label.config(text="조회중")

            status = self.check_instagram(username)
            results.append([username, status])

            self.status_label.config(text=status)
            self.progress_label.config(text=f"{idx+1} / {total}")

            # Save progress
            if progress_path:
                with open(progress_path, "w", encoding="utf-8") as pf:
                    pf.write(str(idx + 1))

            # Sleep
            sleep_time = round(random.uniform(min_sleep, max_sleep), 1)
            time.sleep(sleep_time)

            count_since_long_break += 1
            if count_since_long_break >= next_long_break:
                self.status_label.config(text="장기 휴식")
                time.sleep(long_sleep)
                count_since_long_break = 0
                next_long_break = random.randint(min_count, max_count)

        # Save results
        with open(result_path, "w", newline="", encoding="utf-8") as rf:
            writer = csv.writer(rf)
            writer.writerow(["username", "status"])
            writer.writerows(results)

        self.status_label.config(text="완료")
        self.message_label.config(text="작업 종료")


if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramChecker(root)
    root.mainloop()
