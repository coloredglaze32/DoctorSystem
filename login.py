# login.py
import tkinter as tk
from tkinter import messagebox
from config import USERNAME, PASSWORD

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        self.master.title("中医诊所系统 - 登录")
        self.master.geometry("400x200")  # 修改窗口大小 (原300x150 -> 400x200)
        
        # 用户名标签和输入框
        tk.Label(self.master, text="用户名:").pack(pady=5)
        self.username_entry = tk.Entry(self.master, width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "doctor")  # 设置默认用户名 (新增)
        
        # 密码标签和输入框
        tk.Label(self.master, text="密码:").pack(pady=5)
        self.password_entry = tk.Entry(self.master, show="*", width=25)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "123456")  # 设置默认密码 (新增)
        
        # 登录按钮
        tk.Button(self.master, text="登录", command=self.check_login).pack(pady=10)
        
        # 默认焦点
        self.username_entry.focus()
    
    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == USERNAME and password == PASSWORD:
            self.master.destroy()
            self.on_success()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

def show_login_window(on_success):
    """显示登录窗口"""
    root = tk.Tk()
    app = LoginWindow(root, on_success)
    root.mainloop()