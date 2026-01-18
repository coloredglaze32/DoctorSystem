# login.py
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
from config import USERNAME, PASSWORD

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        
        # 使用ttkbootstrap主题
        self.style = Style(theme="superhero")  # 使用superhero主题，更现代美观
        
        # 设置主窗口
        self.master.title("中医诊所系统 - 登录")
        self.master.geometry("400x300")
        self.master.resizable(False, False)
        
        # 居中窗口
        self.center_window()
        
        # 创建主容器框架
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="中医诊所系统", 
            font=("微软雅黑", 20, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # 用户名输入区域
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(username_frame, text="用户名:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(username_frame, font=("微软雅黑", 10))
        self.username_entry.pack(fill=tk.X, ipady=5)
        self.username_entry.insert(0, "doctor")  # 设置默认用户名
        
        # 密码输入区域
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(password_frame, text="密码:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(password_frame, show="*", font=("微软雅黑", 10))
        self.password_entry.pack(fill=tk.X, ipady=5)
        self.password_entry.insert(0, "123456")  # 设置默认密码
        
        # 登录按钮
        self.login_button = ttk.Button(
            main_frame, 
            text="登录",
            command=self.check_login,
            bootstyle="success-outline"
        )
        self.login_button.pack(pady=20, fill=tk.X, ipady=5)
        
        # 默认焦点
        self.username_entry.focus()
        
        # 绑定回车键登录
        self.password_entry.bind('<Return>', lambda event: self.check_login())
    
    def center_window(self):
        """居中显示窗口"""
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (self.master.winfo_width() // 2)
        y = (self.master.winfo_screenheight() // 2) - (self.master.winfo_height() // 2)
        self.master.geometry(f"{self.master.winfo_width()}x{self.master.winfo_height()}+{x}+{y}")
    
    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if username == USERNAME and password == PASSWORD:
            # 先调用成功回调，再销毁窗口，避免UI组件初始化错误
            self.on_success()
            # 延迟销毁窗口，确保其他组件已正确初始化
            self.master.after(100, self.master.destroy)
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

def show_login_window(on_success):
    """显示登录窗口"""
    root = tk.Tk()
    app = LoginWindow(root, on_success)
    root.mainloop()