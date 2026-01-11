# main.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
from login import show_login_window
from patient import PatientManagementWindow
from database import init_db

# 动态导入，避免循环导入
def get_medical_record_window():
    from medical_record import MedicalRecordWindow
    return MedicalRecordWindow

def get_prescription_window():
    from prescription import PrescriptionWindow
    return PrescriptionWindow

def get_medicine_window():
    from medicine import MedicineWindow
    return MedicineWindow

def main():
    # 初始化数据库
    init_db()
    
    # 显示登录窗口
    show_login_window(lambda: show_main_app())

def show_main_app():
    """显示主应用程序窗口"""
    # 创建主窗口，使用ttkbootstrap样式
    root = ttk.Window(themename="flatly")
    root.title("中医诊所管理系统")
    root.geometry("1200x700")
    
    # 配置Treeview的交替行颜色样式
    style = Style()
    style.configure("evenrow.Treeview", background="#f0f0f0", foreground="black")
    style.configure("oddrow.Treeview", background="white", foreground="black")
    
    # 创建样式化标题栏
    header_frame = ttk.Frame(root, bootstyle="primary")
    header_frame.pack(fill="x", pady=(0, 10))
    
    title_label = ttk.Label(
        header_frame, 
        text="中医诊所管理系统", 
        font=("微软雅黑", 18, "bold"),
        bootstyle="inverse-light"
    )
    title_label.pack(pady=15)
    
    # 主内容区域
    content_frame = ttk.Frame(root)
    content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # 创建菜单
    menu = tk.Menu(root, font=("微软雅黑", 10))
    
    # 文件菜单
    file_menu = tk.Menu(menu, tearoff=0, font=("微软雅黑", 10))
    file_menu.add_command(label="导出所有数据", command=lambda: export_all_data(content_frame))
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)
    menu.add_cascade(label="文件", menu=file_menu)
    
    # 患者菜单 - 直接跳转到患者管理
    menu.add_command(label="患者", command=lambda: show_patient_management(content_frame))
    
    # 病历菜单 - 直接跳转到病历管理
    menu.add_command(label="病历", command=lambda: show_medical_record(content_frame))
    
    # 处方菜单 - 直接跳转到处方管理
    menu.add_command(label="处方", command=lambda: show_prescription(content_frame))
    
    # 药品菜单 - 直接跳转到药品管理
    menu.add_command(label="药品", command=lambda: show_medicine(content_frame))
    
    # 导出菜单
    menu.add_command(label="导出", command=lambda: export_all_data(content_frame))
    
    # 数据可视化菜单
    menu.add_command(label="数据可视化", command=lambda: show_data_visualization(content_frame))
    
    # 设置菜单
    root.config(menu=menu)
    
    # 默认显示患者管理界面
    show_patient_management(content_frame)
    
    # 运行主循环
    root.mainloop()

def clear_frame(frame):
    """清空框架中的所有内容"""
    for widget in frame.winfo_children():
        widget.destroy()

def show_patient_management(frame):
    """显示患者管理界面"""
    clear_frame(frame)
    PatientManagementWindow(frame)

def show_medical_record(frame):
    """显示病历管理界面"""
    clear_frame(frame)
    MedicalRecordWindow = get_medical_record_window()
    MedicalRecordWindow(frame)

def show_prescription(frame):
    """显示处方管理界面"""
    clear_frame(frame)
    PrescriptionWindow = get_prescription_window()
    PrescriptionWindow(frame)

def show_medicine(frame):
    """显示药品管理界面"""
    clear_frame(frame)
    MedicineWindow = get_medicine_window()
    MedicineWindow(frame)

def export_all_data(frame):
    """导出所有数据"""
    # 导入病历窗口以使用其导出功能
    MedicalRecordWindow = get_medical_record_window()
    # 创建一个临时窗口实例来调用导出功能
    temp_window = tk.Toplevel()
    temp_window.withdraw()  # 隐藏窗口
    medical_record_window = MedicalRecordWindow(temp_window)
    medical_record_window.export_patient_data()
    temp_window.destroy()

def show_data_visualization(frame):
    """显示数据可视化界面"""
    clear_frame(frame)
    from data_visualization import DataVisualizationWindow
    # 创建一个独立的窗口而不是在frame中显示，以避免资源清理问题
    visualization_window = tk.Toplevel()
    visualization_window.title("数据可视化")
    visualization_window.geometry("1200x800")
    data_viz = DataVisualizationWindow(visualization_window)
    
    # 设置窗口关闭时的处理
    def on_closing():
        # 手动调用清理函数
        try:
            data_viz.on_destroy(None)
        except:
            pass
        visualization_window.destroy()
    
    visualization_window.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    main()