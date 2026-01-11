# data_visualization.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from database import get_connection
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')  # 使用Tkinter后端
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class DataVisualizationWindow:
    def __init__(self, master):
        self.master = master
        self.create_visualization_interface()
    
    def create_visualization_interface(self):
        """创建数据可视化界面"""
        # 主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_frame, text="数据可视化", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="可视化选项")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # 选择可视化类型
        ttk.Label(control_frame, text="选择图表类型:").pack(side="left", padx=5)
        self.chart_type = ttk.Combobox(control_frame, values=[
            "每日患者数量", 
            "每月患者数量", 
            "每年患者数量",
            "月度趋势图",
            "年度趋势图"
        ], state="readonly", width=15)
        self.chart_type.set("每日患者数量")
        self.chart_type.pack(side="left", padx=5)
        
        # 更新按钮
        ttk.Button(control_frame, text="更新图表", command=self.update_chart).pack(side="left", padx=5)
        
        # 图表显示区域
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建matplotlib图形
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 绑定窗口关闭事件，清理matplotlib资源
        self.master.bind("<Destroy>", self.on_destroy)
        
        # 初始化图表
        self.update_chart()
    
    def on_destroy(self, event):
        """清理资源"""
        if hasattr(self, 'canvas'):
            # 停止任何可能的动画或后台任务
            self.canvas.get_tk_widget().destroy()
        if hasattr(self, 'fig'):
            # 关闭matplotlib图形
            plt.close(self.fig)
            
        # 强制垃圾回收
        import gc
        gc.collect()
    
    def update_chart(self):
        """更新图表"""
        chart_type = self.chart_type.get()
        
        # 清除当前图形
        self.ax.clear()
        
        if chart_type == "每日患者数量":
            self.plot_daily_patients()
        elif chart_type == "每月患者数量":
            self.plot_monthly_patients()
        elif chart_type == "每年患者数量":
            self.plot_yearly_patients()
        elif chart_type == "月度趋势图":
            self.plot_monthly_trend()
        elif chart_type == "年度趋势图":
            self.plot_yearly_trend()
        
        self.canvas.draw()
    
    def plot_daily_patients(self):
        """绘制每日患者数量图"""
        # 获取最近30天的数据
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取最近30天的患者访问数据
        cursor.execute("""
            SELECT date, COUNT(*) as patient_count
            FROM medical_records
            WHERE date >= date('now', '-30 days')
            GROUP BY date
            ORDER BY date
        """)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            dates = [item[0] for item in results]
            counts = [item[1] for item in results]
            
            self.ax.plot(dates, counts, marker='o', linewidth=2, markersize=6)
            self.ax.set_title("最近30天每日患者数量")
            self.ax.set_xlabel("日期")
            self.ax.set_ylabel("患者数量")
            self.ax.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
        else:
            self.ax.text(0.5, 0.5, "暂无数据", horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14)
            self.ax.set_title("最近30天每日患者数量")
        
        self.fig.tight_layout()
    
    def plot_monthly_patients(self):
        """绘制每月患者数量图"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取最近12个月的数据
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as patient_count
            FROM medical_records
            WHERE date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
        """)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            months = [item[0] for item in results]
            counts = [item[1] for item in results]
            
            self.ax.bar(months, counts, color='skyblue', edgecolor='navy', alpha=0.7)
            self.ax.set_title("最近12个月每月患者数量")
            self.ax.set_xlabel("月份")
            self.ax.set_ylabel("患者数量")
            plt.xticks(rotation=45)
        else:
            self.ax.text(0.5, 0.5, "暂无数据", horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14)
            self.ax.set_title("最近12个月每月患者数量")
        
        self.fig.tight_layout()
    
    def plot_yearly_patients(self):
        """绘制每年患者数量图"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取所有年份的数据
        cursor.execute("""
            SELECT strftime('%Y', date) as year, COUNT(*) as patient_count
            FROM medical_records
            GROUP BY strftime('%Y', date)
            ORDER BY year
        """)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            years = [item[0] for item in results]
            counts = [item[1] for item in results]
            
            self.ax.bar(years, counts, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
            self.ax.set_title("年度患者数量")
            self.ax.set_xlabel("年份")
            self.ax.set_ylabel("患者数量")
        else:
            self.ax.text(0.5, 0.5, "暂无数据", horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14)
            self.ax.set_title("年度患者数量")
    
    def plot_monthly_trend(self):
        """绘制月度趋势图"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取最近12个月的数据
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as patient_count
            FROM medical_records
            WHERE date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
        """)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            months = [item[0] for item in results]
            counts = [item[1] for item in results]
            
            self.ax.plot(months, counts, marker='o', linewidth=2, markersize=6, color='red')
            self.ax.set_title("最近12个月患者数量趋势")
            self.ax.set_xlabel("月份")
            self.ax.set_ylabel("患者数量")
            self.ax.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
        else:
            self.ax.text(0.5, 0.5, "暂无数据", horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14)
            self.ax.set_title("最近12个月患者数量趋势")
        
        self.fig.tight_layout()
    
    def plot_yearly_trend(self):
        """绘制年度趋势图"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取所有年份的数据
        cursor.execute("""
            SELECT strftime('%Y', date) as year, COUNT(*) as patient_count
            FROM medical_records
            GROUP BY strftime('%Y', date)
            ORDER BY year
        """)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            years = [item[0] for item in results]
            counts = [item[1] for item in results]
            
            self.ax.plot(years, counts, marker='o', linewidth=2, markersize=6, color='orange')
            self.ax.set_title("年度患者数量趋势")
            self.ax.set_xlabel("年份")
            self.ax.set_ylabel("患者数量")
            self.ax.grid(True, linestyle='--', alpha=0.6)
        else:
            self.ax.text(0.5, 0.5, "暂无数据", horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14)
            self.ax.set_title("年度患者数量趋势")