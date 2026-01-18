# patient.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class PatientManagementWindow:
    def __init__(self, master):
        self.master = master
        # 不再创建新窗口，使用传入的master作为主界面
        # 创建按钮区域
        self.create_buttons()
        
        # 创建查询表单
        self.create_search_form()
        
        # 创建患者列表区域
        self.create_patient_list()
        
        # 加载患者数据
        self.load_patients()
    
    def create_buttons(self):
        """创建按钮区域"""
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="新建患者", command=self.open_create_window).pack(side="left", padx=5)
    
    def create_search_form(self):
        """创建查询表单"""
        search_frame = ttk.LabelFrame(self.master, text="查询条件")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 姓名查询
        ttk.Label(search_frame, text="姓名:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.name_search = ttk.Entry(search_frame, width=15, font=("微软雅黑", 10))
        self.name_search.grid(row=0, column=1, padx=5, pady=10)
        
        # 手机号查询
        ttk.Label(search_frame, text="手机号:", font=("微软雅黑", 10, "bold")).grid(row=0, column=2, padx=5, pady=10, sticky="e")
        self.phone_search = ttk.Entry(search_frame, width=15, font=("微软雅黑", 10))
        self.phone_search.grid(row=0, column=3, padx=5, pady=10)
        
        # 年龄查询
        ttk.Label(search_frame, text="年龄:", font=("微软雅黑", 10, "bold")).grid(row=0, column=4, padx=5, pady=10, sticky="e")
        self.age_search = ttk.Entry(search_frame, width=10, font=("微软雅黑", 10))
        self.age_search.grid(row=0, column=5, padx=5, pady=10)

        # 查询按钮
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=6, columnspan=2, padx=5, pady=10)
        
        ttk.Button(btn_frame, text="查询", command=self.search_patients).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_search).pack(side="left", padx=5)
    
    def create_patient_list(self):
        """创建患者列表"""
        list_frame = ttk.LabelFrame(self.master, text="患者列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ("id", "name", "gender", "age", "phone", "history", "modify", "delete", "export")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题（居中对齐）
        self.tree.heading("id", text="ID", anchor="center")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("name", text="姓名", anchor="center")
        self.tree.column("name", width=100, anchor="center")
        self.tree.heading("gender", text="性别", anchor="center")
        self.tree.column("gender", width=60, anchor="center")
        self.tree.heading("age", text="年龄", anchor="center")
        self.tree.column("age", width=60, anchor="center")
        self.tree.heading("phone", text="手机号", anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.heading("history", text="病史", anchor="center")
        self.tree.column("history", width=150, anchor="center")
        self.tree.heading("modify", text="修改", anchor="center")
        self.tree.column("modify", width=70, anchor="center")
        self.tree.heading("delete", text="删除", anchor="center")
        self.tree.column("delete", width=70, anchor="center")
        self.tree.heading("export", text="导出", anchor="center")
        self.tree.column("export", width=70, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 配置样式以添加交替行颜色
        style = ttk.Style()
        # 定义样式，注意在ttk中需要使用配置方式
        style.configure("Treeview", rowheight=25, font=("微软雅黑", 10))
        style.map("Treeview",
            background=[('selected', '#3a7fd0')],
            foreground=[('selected', 'white')]
        )
        # 为交替行定义样式
        style.configure("Treeview.EvenRow", background="#f8f9fa", foreground="black")
        style.configure("Treeview.OddRow", background="white", foreground="black")
        style.configure("Treeview.Heading", font=("微软雅黑", 10, "bold"), background="#2c3e50", foreground="white")
        
        # 绑定双击事件 - 跳转到病历
        self.tree.bind("<Double-1>", self.on_patient_double_click)
        # 绑定右键事件 - 复制行信息到剪贴板
        self.tree.bind("<Button-3>", self.copy_row_to_clipboard)
        # 绑定左键点击事件 - 仅选择行（不再自动跳转）
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

    def load_patients(self):
        """加载患者数据到列表"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, gender, age, phone, history FROM patients")
        patients = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for index, patient in enumerate(patients):
            # 确保病史字段不为None
            patient_list = list(patient)
            if patient_list[5] is None:  # 病史字段为None时设为空字符串
                patient_list[5] = ""
            # 添加操作按钮的文本（修改、删除和导出）
            patient_with_action = tuple(patient_list) + ("修改", "删除", "导出")
            item_id = self.tree.insert("", "end", values=patient_with_action)
            # 根据行号设置交替颜色
            if index % 2 == 0:
                self.tree.item(item_id, tags=("evenrow",))
            else:
                self.tree.item(item_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.master.update_idletasks()

    def search_patients(self):
        """根据条件查询患者"""
        name = self.name_search.get().strip()
        phone = self.phone_search.get().strip()
        age = self.age_search.get().strip()

        conn = get_connection()
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")

        if phone:
            conditions.append("phone LIKE ?")
            params.append(f"%{phone}%")

        if age:
            conditions.append("age = ?")
            params.append(age)

        if conditions:
            query = f"SELECT id, name, gender, age, phone, history FROM patients WHERE {' AND '.join(conditions)}"
        else:
            query = "SELECT id, name, gender, age, phone, history FROM patients"

        cursor.execute(query, params)
        patients = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加查询结果
        for index, patient in enumerate(patients):
            # 确保病史字段不为None
            patient_list = list(patient)
            if patient_list[5] is None:  # 病史字段为None时设为空字符串
                patient_list[5] = ""
            # 添加操作按钮的文本（修改、删除和导出）
            patient_with_action = tuple(patient_list) + ("修改", "删除", "导出")
            item_id = self.tree.insert("", "end", values=patient_with_action)
            # 根据行号设置交替颜色
            if index % 2 == 0:
                self.tree.item(item_id, tags=("evenrow",))
            else:
                self.tree.item(item_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.master.update_idletasks()

    def on_tree_click(self, event):
        """处理树形视图点击事件"""
        # 获取点击的行和列
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        
        if row:
            # 选中该行
            self.tree.selection_set(row)
            
            # 获取该行的数据
            values = self.tree.item(row, "values")
            patient_id = values[0]
            patient_name = values[1]
            patient_gender = values[2]
            patient_age = values[3]
            patient_phone = values[4]
            patient_history = values[5]
            
            # 根据点击的列执行相应操作
            if col == "#7":  # 修改列
                self.open_edit_window(patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history)
            elif col == "#8":  # 删除列
                self.delete_patient(patient_id)
            elif col == "#9":  # 导出列
                self.export_single_patient(patient_id)
            # 其他列点击不再自动跳转，改为双击跳转

    def copy_row_to_clipboard(self, event):
        """复制行信息到剪贴板"""
        # 选中点击的行
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            values = self.tree.item(item, "values")
            
            # 将行数据转换为字符串格式（不包含操作列）
            row_str = "\t".join([str(v) for v in values[:6]])  # 只复制前6列数据
            self.master.clipboard_clear()  # 清空剪贴板
            self.master.clipboard_append(row_str)  # 添加到剪贴板
            messagebox.showinfo("提示", "已复制行信息到剪贴板")
    
    def export_single_patient(self, patient_id):
        """导出单个患者的信息，包括病历和处方"""
        from tkinter import filedialog
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="保存患者信息"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                # 获取患者信息
                conn = get_connection()
                cursor = conn.cursor()
                
                # 查询患者基本信息
                cursor.execute("SELECT id, name, gender, age, phone, history FROM patients WHERE id = ?", (patient_id,))
                patient = cursor.fetchone()
                
                if patient:
                    f.write(f"患者ID: {patient[0]}\n")
                    f.write(f"姓名: {patient[1]}\n")
                    f.write(f"性别: {patient[2]}\n")
                    f.write(f"年龄: {patient[3]}\n")
                    f.write(f"电话: {patient[4]}\n")
                    f.write(f"病史: {patient[5] if patient[5] else '无'}\n")
                    f.write("-" * 50 + "\n")
                    
                    # 查询患者的病历信息
                    cursor.execute("""
                        SELECT id, date, wang, wen, wen2, qie, diagnosis, treatment
                        FROM medical_records WHERE patient_id = ?
                        ORDER BY date DESC
                    """, (patient_id,))
                    records = cursor.fetchall()
                    
                    if records:
                        for record in records:
                            f.write(f"  病历ID: {record[0]}\n")
                            f.write(f"  日期: {record[1]}\n")
                            f.write(f"  望诊: {record[2] if record[2] else '无'}\n")
                            f.write(f"  闻诊: {record[3] if record[3] else '无'}\n")
                            f.write(f"  问诊: {record[4] if record[4] else '无'}\n")
                            f.write(f"  切诊: {record[5] if record[5] else '无'}\n")
                            f.write(f"  诊断: {record[6] if record[6] else '无'}\n")
                            f.write(f"  治疗方案: {record[7] if record[7] else '无'}\n")
                            
                            # 查询该病历的处方
                            cursor.execute("""
                                SELECT medicine, dosage, usage
                                FROM prescriptions WHERE record_id = ?
                            """, (record[0],))
                            prescriptions = cursor.fetchall()
                            
                            if prescriptions:
                                f.write("  处方:\n")
                                for pres in prescriptions:
                                    f.write(f"    - 药品: {pres[0]}, 剂量: {pres[1]}, 用法: {pres[2]}\n")
                            else:
                                f.write("  处方: 无\n")
                            
                            f.write("-" * 30 + "\n")
                    else:
                        f.write("  病历: 无\n")
                        f.write("-" * 30 + "\n")
                    
                    conn.close()
                    
                messagebox.showinfo("成功", f"患者信息已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def on_patient_double_click(self, event):
        """处理患者列表项双击事件"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            
            patient_id = values[0]  # ID列的索引是0
            
            # 直接跳转到病历界面
            self.open_medical_record_window(patient_id)


    
    def reset_search(self):
        """重置查询条件"""
        self.name_search.delete(0, tk.END)
        self.phone_search.delete(0, tk.END)
        self.age_search.delete(0, tk.END)
        self.load_patients()

    def open_create_window(self):
        """打开新建患者窗口"""
        CreatePatientWindow(self.master, self)

    def delete_patient(self, patient_id):
        """删除患者"""
        if messagebox.askyesno("确认", "确定要删除该患者吗？"):
            conn = get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                conn.commit()
                messagebox.showinfo("成功", "患者已删除")
                # 重新加载患者列表
                self.load_patients()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
            finally:
                conn.close()

    def show_action_menu(self, patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history):
        """显示操作菜单"""
        # 创建一个简单的菜单来选择操作
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="修改", command=lambda: self.open_edit_window(patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history))
        menu.add_command(label="删除", command=lambda: self.delete_patient(patient_id))
        menu.post(self.master.winfo_pointerx(), self.master.winfo_pointery())
    
    def open_medical_record_window(self, patient_id):
        """打开病历窗口并显示该患者的病历"""
        # 清空当前界面并显示病历界面
        for widget in self.master.winfo_children():
            if widget != self.master.winfo_children()[0]:  # 保留菜单栏
                widget.destroy()
        
        from medical_record import MedicalRecordWindow
        medical_record_window = MedicalRecordWindow(self.master, patient_id=patient_id)

    def open_edit_window(self, patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history):
        """打开编辑患者窗口"""
        EditPatientWindow(self.master, self, patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history)


class CreatePatientWindow:
    def __init__(self, master, parent_window):
        self.parent_window = parent_window
        # 使用主窗口作为父级，而不是传入的master
        self.master = tk.Toplevel(master.winfo_toplevel())
        self.master.title("新建患者")
        self.master.geometry("1200x700")  # 调整窗口尺寸
        self.master.resizable(True, True)
        
        # 防抖变量
        self.debounce_timer = None
        
        # 创建主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 将滚动区域添加到主框架
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建患者信息输入表单
        self.create_patient_form(scrollable_frame)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # 绑定键盘事件
        canvas.bind("<Key>", _on_mousewheel)
        canvas.focus_set()

    def create_patient_form(self, parent_frame):
        """创建患者信息输入表单"""
        # 创建主框架
        main_frame = parent_frame
        
        # 患者信息标签框
        patient_frame = ttk.LabelFrame(main_frame, text="患者基本信息")
        patient_frame.pack(fill="x", padx=5, pady=5)
        
        # 基本信息
        ttk.Label(patient_frame, text="姓名*:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(patient_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.bind('<KeyRelease>', self.check_existing_patient)  # 添加事件监听
        
        ttk.Label(patient_frame, text="性别:", font=("微软雅黑", 9, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.gender_entry = ttk.Combobox(patient_frame, values=["男", "女"], width=5)
        self.gender_entry.grid(row=0, column=3, padx=5, pady=5)
        self.gender_entry.current(0)
        
        ttk.Label(patient_frame, text="年龄:", font=("微软雅黑", 9, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.age_entry = ttk.Entry(patient_frame, width=8)
        self.age_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(patient_frame, text="电话*:", font=("微软雅黑", 9, "bold")).grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(patient_frame, width=15)
        self.phone_entry.grid(row=0, column=7, padx=5, pady=5)
        self.phone_entry.bind('<KeyRelease>', self.check_existing_patient)  # 添加事件监听
        
        # 病史
        ttk.Label(patient_frame, text="病史:", font=("微软雅黑", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.history_text = tk.Text(patient_frame, height=2, width=60)
        self.history_text.grid(row=1, column=1, columnspan=7, padx=5, pady=5)
        self.history_text.config(undo=True)  # 启用撤销功能
        
        # 病历信息标签框
        record_frame = ttk.LabelFrame(main_frame, text="病历信息")
        record_frame.pack(fill="x", padx=5, pady=5)
        
        # 病历基本信息
        ttk.Label(record_frame, text="日期:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        # 创建日期选择按钮
        self.date_frame = ttk.Frame(record_frame)
        self.date_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.date_entry = ttk.Entry(self.date_frame, width=12)
        self.date_entry.pack(side="left")
        
        from datetime import datetime
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 添加日历选择按钮
        date_button = ttk.Button(self.date_frame, text="📅", width=2, command=self.open_date_picker)
        date_button.pack(side="left", padx=(5, 0))
        
        # 望闻问切
        ttk.Label(record_frame, text="望诊:", font=("微软雅黑", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.wang_text = tk.Text(record_frame, height=2, width=30)
        self.wang_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        self.wang_text.config(undo=True)  # 启用撤销功能
        
        ttk.Label(record_frame, text="闻诊:", font=("微软雅黑", 9, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.wen_text = tk.Text(record_frame, height=2, width=30)
        self.wen_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        self.wen_text.config(undo=True)  # 启用撤销功能
        
        ttk.Label(record_frame, text="问诊:", font=("微软雅黑", 9, "bold")).grid(row=3, column=0, padx=5, pady=5, sticky="ne")
        self.wen2_text = tk.Text(record_frame, height=2, width=30)
        self.wen2_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)
        self.wen2_text.config(undo=True)  # 启用撤销功能
        
        ttk.Label(record_frame, text="切诊:", font=("微软雅黑", 9, "bold")).grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        self.qie_text = tk.Text(record_frame, height=2, width=30)
        self.qie_text.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        self.qie_text.config(undo=True)  # 启用撤销功能
        
        # 诊断和治疗方案
        ttk.Label(record_frame, text="诊断*:", font=("微软雅黑", 9, "bold")).grid(row=5, column=0, padx=5, pady=5, sticky="ne")
        self.diagnosis_text = tk.Text(record_frame, height=2, width=60)
        self.diagnosis_text.grid(row=5, column=1, columnspan=3, padx=5, pady=5)
        self.diagnosis_text.config(undo=True)  # 启用撤销功能
        
        ttk.Label(record_frame, text="治疗方案:", font=("微软雅黑", 9, "bold")).grid(row=6, column=0, padx=5, pady=5, sticky="ne")
        self.treatment_text = tk.Text(record_frame, height=2, width=60)
        self.treatment_text.grid(row=6, column=1, columnspan=3, padx=5, pady=5)
        self.treatment_text.config(undo=True)  # 启用撤销功能
        
        # 处方信息标签框
        prescription_frame = ttk.LabelFrame(main_frame, text="处方信息")
        prescription_frame.pack(fill="x", padx=5, pady=5)
        
        # 处方输入区域
        prescription_input_frame = ttk.Frame(prescription_frame)
        prescription_input_frame.pack(fill="x", padx=5, pady=5)
        
        # 药品选择
        ttk.Label(prescription_input_frame, text="药品:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        # 创建药品选择框架
        medicine_frame = ttk.Frame(prescription_input_frame)
        medicine_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(medicine_frame, textvariable=self.medicine_var, width=15)
        self.medicine_combo.pack(side="left")
        
        # 库存标签
        self.stock_label = ttk.Label(medicine_frame, text="", foreground="gray")
        self.stock_label.pack(side="left", padx=(5, 0))
        
        # 绑定药品选择变化事件
        self.medicine_var.trace_add('write', self.on_medicine_selected)
        
        # 剂量
        ttk.Label(prescription_input_frame, text="剂量:", font=("微软雅黑", 9, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.dosage_entry = ttk.Entry(prescription_input_frame, width=10)
        self.dosage_entry.grid(row=0, column=3, padx=5, pady=5)
        self.setup_entry_undo(self.dosage_entry)  # 启用撤销功能
        
        # 绑定剂量输入事件以实时更新库存显示
        self.dosage_entry.bind('<KeyRelease>', self.on_dosage_change)
        
        # 用法
        ttk.Label(prescription_input_frame, text="用法:", font=("微软雅黑", 9, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.usage_entry = ttk.Entry(prescription_input_frame, width=15)
        self.usage_entry.grid(row=0, column=5, padx=5, pady=5)
        self.setup_entry_undo(self.usage_entry)  # 启用撤销功能
        
        # 添加按钮
        ttk.Button(prescription_input_frame, text="添加药品", command=self.add_medicine_to_list).grid(row=0, column=6, padx=5, pady=5)
        
        # 处方列表
        self.prescription_list_frame = ttk.LabelFrame(prescription_frame, text="处方列表")
        self.prescription_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建处方列表树形视图
        columns = ("药品", "剂量", "用法")
        self.prescription_tree = ttk.Treeview(self.prescription_list_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # 设置列标题（左对齐）
        for col in columns:
            self.prescription_tree.heading(col, text=col, anchor="w")
            self.prescription_tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.prescription_list_frame, orient="vertical", command=self.prescription_tree.yview)
        self.prescription_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.prescription_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 配置样式以添加交替行颜色
        style = ttk.Style()
        # 定义样式，注意在ttk中需要使用配置方式
        style.configure("Custom.Treeview", rowheight=25)
        style.map("Custom.Treeview",
            background=[('selected', '#3a7fd0')],
            foreground=[('selected', 'white')]
        )
        # 为交替行定义样式
        style.configure("evenrow.Treeview", background="#f0f0f0", foreground="black")
        style.configure("oddrow.Treeview", background="white", foreground="black")
        style.configure("Custom.Treeview.Heading", anchor="w")
        
        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="保存", command=self.save_patient_and_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=self.master.destroy).pack(side="left", padx=5)
        
        # 加载药品列表
        self.load_medicines()
        
        # 为输入框添加撤销/重做功能
        self.setup_entry_undo(self.name_entry)
        self.setup_entry_undo(self.age_entry)
        self.setup_entry_undo(self.phone_entry)
        self.setup_entry_undo(self.date_entry)
        self.setup_entry_undo(self.dosage_entry)
        self.setup_entry_undo(self.usage_entry)
    
    def on_medicine_selected(self, *args):
        """当药品选择发生变化时，更新库存和用法显示"""
        medicine_name = self.medicine_var.get().strip()
        if medicine_name:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT stock, unit, usage FROM medicines WHERE name = ?", (medicine_name,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                stock, unit, usage = result
                self.stock_label.config(text=f"库存: {stock}{unit}")
                # 自动填充用法字段
                if usage:
                    self.usage_entry.delete(0, tk.END)
                    self.usage_entry.insert(0, usage)
            else:
                self.stock_label.config(text="未找到药品")
        else:
            self.stock_label.config(text="")
    
    def on_dosage_change(self, event):
        """当剂量发生变化时，更新库存显示"""
        self.on_medicine_selected()
    
    def setup_entry_undo(self, entry):
        """为Entry控件添加撤销/重做功能"""
        # 创建撤销栈
        entry.history = []
        entry.history_index = -1
        entry.max_history = 50
        
        def on_key_press(event):
            # 记录当前状态
            current_value = entry.get()
            if (entry.history_index == -1 or 
                entry.history[entry.history_index] != current_value):
                # 清除当前索引之后的历史
                entry.history = entry.history[:entry.history_index + 1]
                # 添加当前状态
                entry.history.append(current_value)
                entry.history_index += 1
                # 限制历史记录大小
                if len(entry.history) > entry.max_history:
                    entry.history.pop(0)
                    entry.history_index -= 1
        
        def on_undo(event=None):
            if entry.history_index > 0:
                entry.history_index -= 1
                entry.delete(0, tk.END)
                entry.insert(0, entry.history[entry.history_index])
        
        def on_redo(event=None):
            if entry.history_index < len(entry.history) - 1:
                entry.history_index += 1
                entry.delete(0, tk.END)
                entry.insert(0, entry.history[entry.history_index])
        
        # 绑定事件
        entry.bind('<Control-z>', on_undo)
        entry.bind('<Control-y>', on_redo)
        entry.bind('<KeyRelease>', on_key_press)
        
        # 记录初始状态
        entry.history.append(entry.get())
    
    def open_date_picker(self):
        """打开日期选择器"""
        # 创建日期选择窗口
        date_window = tk.Toplevel(self.master)
        date_window.title("选择日期")
        date_window.geometry("300x250")
        date_window.transient(self.master)
        date_window.grab_set()  # 模态窗口
        
        # 使用日历组件
        try:
            import calendar
            from tkinter import simpledialog
            
            # 获取当前日期
            current_date = self.date_entry.get()
            try:
                import datetime
                date_parts = current_date.split('-')
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])
            except:
                from datetime import datetime
                now = datetime.now()
                year = now.year
                month = now.month
                day = now.day
            
            # 创建日历显示
            cal_frame = ttk.Frame(date_window)
            cal_frame.pack(pady=10)
            
            # 年份和月份选择
            nav_frame = ttk.Frame(cal_frame)
            nav_frame.grid(row=0, column=0, columnspan=7, pady=5)
            
            year_var = tk.IntVar(value=year)
            month_var = tk.IntVar(value=month)
            
            ttk.Button(nav_frame, text="<", command=lambda: self.change_month(-1, year_var, month_var, cal_frame)).pack(side="left")
            ttk.Label(nav_frame, textvariable=year_var).pack(side="left", padx=5)
            ttk.Label(nav_frame, text="年").pack(side="left")
            ttk.Label(nav_frame, textvariable=month_var).pack(side="left", padx=5)
            ttk.Label(nav_frame, text="月").pack(side="left")
            ttk.Button(nav_frame, text=">", command=lambda: self.change_month(1, year_var, month_var, cal_frame)).pack(side="left")
            
            # 星期标题
            weekdays = ['一', '二', '三', '四', '五', '六', '日']
            for i, day in enumerate(weekdays):
                ttk.Label(cal_frame, text=day, font=('TkDefaultFont', 9, 'bold')).grid(row=1, column=i, padx=2, pady=2)
            
            # 显示当前月份的日历
            self.show_month(year, month, day, cal_frame, date_window)
            
        except ImportError:
            # 如果没有日历组件，使用简单的输入方式
            from tkinter import simpledialog
            result = simpledialog.askstring("输入日期", "请输入日期 (YYYY-MM-DD):", initialvalue=self.date_entry.get())
            if result:
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, result)
    
    def change_month(self, direction, year_var, month_var, cal_frame):
        """改变月份"""
        month = month_var.get() + direction
        year = year_var.get()
        
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        
        month_var.set(month)
        year_var.set(year)
        
        # 清除日历显示（保留标题行）
        for widget in cal_frame.grid_slaves():
            if int(widget.grid_info()['row']) > 1:
                widget.destroy()
        
        # 重新显示日历，此时date_window为None，因为我们只是更新日历
        self.show_month(year, month, 1, cal_frame, None, update_only=True)
    
    def show_month(self, year, month, selected_day, cal_frame, date_window, update_only=False):
        """显示月份日历"""
        import calendar
        from datetime import datetime
        
        # 获取月份信息
        cal = calendar.monthcalendar(year, month)
        
        # 显示日期按钮
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day != 0:  # 非零表示有效日期
                    # 如果date_window为None，我们只是更新日历而不关闭窗口
                    if date_window:
                        btn_command = lambda d=day, m=month, y=year, w=date_window: self.select_date(d, m, y, w)
                    else:
                        btn_command = lambda d=day, m=month, y=year: self.update_date_entry(d, m, y)
                    
                    btn = ttk.Button(
                        cal_frame,
                        text=str(day),
                        width=3,
                        command=btn_command
                    )
                    btn.grid(row=week_idx+2, column=day_idx, padx=2, pady=2)
                    
                    # 高亮选中日期
                    if day == selected_day:
                        btn.state(['active'])
                else:
                    # 空白格子
                    ttk.Label(cal_frame, text="  ", width=3).grid(row=week_idx+2, column=day_idx, padx=2, pady=2)
    
    def select_date(self, day, month, year, date_window):
        """选择日期"""
        selected_date = f"{year}-{month:02d}-{day:02d}"
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, selected_date)
        date_window.destroy()
    
    def update_date_entry(self, day, month, year):
        """更新日期输入框（不关闭窗口）"""
        selected_date = f"{year}-{month:02d}-{day:02d}"
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, selected_date)
    
    def load_medicines(self):
        """加载药品列表到下拉框"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM medicines")
        medicines = cursor.fetchall()
        conn.close()
        
        # 填充药品下拉框
        medicine_names = [med[0] for med in medicines]
        self.medicine_combo['values'] = medicine_names
        
        # 设置自动完成
        self.setup_autocomplete(self.medicine_combo, medicine_names)
    
    def setup_autocomplete(self, combobox, choices):
        """设置下拉框的自动完成功能"""
        def autocomplete(event):
            if event.keysym not in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab']:
                text = combobox.get().lower()
                if text:
                    # 查找匹配的选项
                    matches = [choice for choice in choices if text in choice.lower()]
                    if matches:
                        # 设置下拉框的值为匹配项
                        combobox['values'] = matches
                        combobox.event_generate('<Down>')  # 显示下拉列表
                else:
                    # 如果输入为空，显示所有选项
                    combobox['values'] = choices
        
        # 绑定事件
        combobox.bind('<KeyRelease>', autocomplete)
        combobox.bind('<FocusIn>', lambda e: combobox['values'] == choices)
    
    def add_medicine_to_list(self):
        """添加药品到处方列表"""
        medicine = self.medicine_var.get()
        dosage = self.dosage_entry.get()
        usage = self.usage_entry.get()
        
        if not medicine:
            messagebox.showerror("错误", "请选择药品")
            return
        
        # 检查药品是否存在于药品表中
        if not self.is_medicine_exists(medicine):
            messagebox.showerror("错误", f"药品 '{medicine}' 不存在，请从已有药品中选择")
            return
        
        if not dosage:
            dosage = "适量"
        
        if not usage:
            usage = ""  # 如果没有输入用法，保存为空
        
        # 检查库存是否足够
        if not self.check_medicine_stock(medicine, dosage):
            return
        
        # 添加到列表
        item_id = self.prescription_tree.insert("", "end", values=(medicine, dosage, usage))
        
        # 应用交替行颜色
        children = self.prescription_tree.get_children('')
        for i, child_id in enumerate(children):
            if i % 2 == 0:
                self.prescription_tree.item(child_id, tags=("evenrow",))
            else:
                self.prescription_tree.item(child_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.prescription_list_frame.update_idletasks()
        
        # 清空输入框
        self.medicine_var.set("")
        self.dosage_entry.delete(0, tk.END)
        self.usage_entry.delete(0, tk.END)
    
    def check_medicine_stock(self, medicine_name, dosage):
        """检查药品库存是否足够"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 查询药品库存信息
            cursor.execute("SELECT stock, unit FROM medicines WHERE name = ?", (medicine_name,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("错误", f"未找到药品 '{medicine_name}'")
                return False
            
            stock, unit = result
            
            # 尝试解析剂量，提取数字部分
            try:
                # 提取剂量中的数字部分
                dosage_number = float(''.join([c for c in dosage if c.isdigit() or c == '.']).strip())
            except ValueError:
                messagebox.showerror("错误", f"剂量格式不正确: {dosage}")
                return False
            
            if dosage_number > stock:
                messagebox.showerror("错误", f"库存不足！{medicine_name} 当前库存为 {stock}{unit}，请求 {dosage_number}{unit}")
                return False
            
            return True
        finally:
            conn.close()
    
    def is_medicine_exists(self, medicine_name):
        """检查药品是否存在于药品表中"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM medicines WHERE name = ?", (medicine_name,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()
    
    def save_patient_and_record(self):
        """保存患者、病历和处方信息"""
        # 获取患者信息
        name = self.name_entry.get().strip()
        gender = self.gender_entry.get()
        age = self.age_entry.get()
        phone = self.phone_entry.get()
        history = self.history_text.get("1.0", "end").strip()
        
        # 必填项验证
        if not name:
            messagebox.showerror("错误", "姓名为必填项，请填写患者姓名")
            self.name_entry.focus_set()  # 将焦点设置到姓名输入框
            return
        
        if not phone:
            messagebox.showerror("错误", "电话为必填项，请填写患者电话")
            self.phone_entry.focus_set()  # 将焦点设置到电话输入框
            return
        
        # 获取病历信息
        date = self.date_entry.get()
        wang = self.wang_text.get("1.0", "end").strip()
        wen = self.wen_text.get("1.0", "end").strip()
        wen2 = self.wen2_text.get("1.0", "end").strip()
        qie = self.qie_text.get("1.0", "end").strip()
        diagnosis = self.diagnosis_text.get("1.0", "end").strip()
        treatment = self.treatment_text.get("1.0", "end").strip()
        
        if not diagnosis:
            messagebox.showerror("错误", "诊断为必填项，请填写诊断结果")
            self.diagnosis_text.focus_set()  # 将焦点设置到诊断输入框
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在同名患者（姓名和电话都匹配）
            cursor.execute("SELECT id, history FROM patients WHERE name = ? AND phone = ?", (name, phone))
            existing = cursor.fetchone()
            
            if existing:
                # 更新患者信息，但保留原有病史（如果新输入的病史为空）
                patient_id = existing[0]
                existing_history = existing[1] or ""
                
                # 如果新输入的病史为空，使用原有病史
                if not history.strip():
                    history = existing_history
                
                cursor.execute("""
                    UPDATE patients SET gender = ?, age = ?, phone = ?, history = ?
                    WHERE id = ?
                """, (gender, age, phone, history, patient_id))
                
                messagebox.showinfo("成功", "患者信息已更新，病历信息已保存")
            else:
                # 新增患者
                cursor.execute("""
                    INSERT INTO patients (name, gender, age, phone, history)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, gender, age, phone, history))
                patient_id = cursor.lastrowid
                messagebox.showinfo("成功", "患者信息已保存")
            
            # 保存病历
            cursor.execute("""
                INSERT INTO medical_records (patient_id, date, wang, wen, wen2, qie, diagnosis, treatment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, date, wang, wen, wen2, qie, diagnosis, treatment))
            
            # 获取新插入的病历ID
            record_id = cursor.lastrowid
            
            # 保存处方
            prescriptions_to_update = []
            for item in self.prescription_tree.get_children():
                values = self.prescription_tree.item(item, "values")
                medicine, dosage, usage = values
                cursor.execute("""
                    INSERT INTO prescriptions (record_id, medicine, dosage, usage)
                    VALUES (?, ?, ?, ?)
                """, (record_id, medicine, dosage, usage))
                
                # 记录需要更新库存的药品信息
                prescriptions_to_update.append((medicine, dosage))
            
            conn.commit()
            
            # 提交处方信息后，再更新药品库存
            for medicine, dosage in prescriptions_to_update:
                self.update_medicine_stock(medicine, dosage)
            
            messagebox.showinfo("成功", "患者、病历和处方信息已保存")
            
            # 关闭窗口
            self.master.destroy()
            
            # 刷新父窗口的患者列表
            self.parent_window.load_patients()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("错误", f"保存失败: {str(e)}")
        finally:
            conn.close()
    
    def update_medicine_stock(self, medicine_name, dosage):
        """更新药品库存"""
        try:
            # 尝试解析剂量中的数字部分
            dosage_number = float(''.join([c for c in dosage if c.isdigit() or c == '.']).strip())
        except ValueError:
            # 如果无法解析剂量，跳过库存更新
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取当前库存
            cursor.execute("SELECT stock FROM medicines WHERE name = ?", (medicine_name,))
            result = cursor.fetchone()
            
            if result:
                current_stock = result[0]
                new_stock = max(0, current_stock - dosage_number)  # 防止库存变为负数
                
                # 更新库存
                cursor.execute("UPDATE medicines SET stock = ? WHERE name = ?", (new_stock, medicine_name))
                conn.commit()
        except Exception as e:
            # 发生错误时不中断主要流程
            print(f"更新库存失败: {e}")
        finally:
            conn.close()
    
    def clear_form(self):
        """清空表单"""
        self.name_entry.delete(0, tk.END)
        self.gender_entry.current(0)
        self.age_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.history_text.delete("1.0", tk.END)
        
        self.date_entry.delete(0, tk.END)
        from datetime import datetime
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.wang_text.delete("1.0", tk.END)
        self.wen_text.delete("1.0", tk.END)
        self.wen2_text.delete("1.0", tk.END)
        self.qie_text.delete("1.0", tk.END)
        self.diagnosis_text.delete("1.0", tk.END)
        self.treatment_text.delete("1.0", tk.END)
        
        self.medicine_var.set("")
        self.dosage_entry.delete(0, tk.END)
        self.usage_entry.delete(0, tk.END)
        
        # 清空处方列表
        for item in self.prescription_tree.get_children():
            self.prescription_tree.delete(item)
    
    def check_existing_patient(self, event=None):
        """检查是否已存在相同姓名和电话的患者"""
        # 打印调试信息，确认事件被触发
        print(f"check_existing_patient triggered. Name: '{self.name_entry.get().strip()}', Phone: '{self.phone_entry.get().strip()}'")
        
        # 直接执行检查，不再使用防抖
        self._perform_check_existing_patient()
    
    def _perform_check_existing_patient(self):
        """实际执行检查的方法"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        print(f"_perform_check_existing_patient called. Name: '{name}', Phone: '{phone}'")
        
        # 只有当姓名和电话都填写完整时才检查
        if name and phone:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT history FROM patients WHERE name = ? AND phone = ?", (name, phone))
                existing = cursor.fetchone()
                print(f"Database query result: {existing}")
                
                if existing and existing[0]:  # 如果找到了现有患者且有病史
                    print(f"Found existing patient history: {existing[0][:50]}...")
                    # 自动填充病史
                    self.history_text.delete("1.0", tk.END)
                    self.history_text.insert("1.0", existing[0])
                    
                    # 提示信息
                    messagebox.showinfo("提示", "检测到该患者已存在，病史已自动填充")
                else:
                    print("No existing patient found or no history")
                    # 如果没有找到现有患者，且病史文本框中有内容，询问是否清空
                    current_history = self.history_text.get("1.0", "end").strip()
                    if current_history:
                        # 可以选择保留当前病史或清空
                        pass  # 暂时不处理
            except Exception as e:
                print(f"查询患者信息时出错: {e}")
            finally:
                conn.close()
        else:
            print("Name or phone is empty, skipping query")
            # 如果姓名或电话为空，不清空病史（可能用户正在输入）
            pass

class EditPatientWindow:
    def __init__(self, master, parent_window, patient_id, patient_name, patient_gender, patient_age, patient_phone, patient_history):
        self.parent_window = parent_window
        self.patient_id = patient_id
        # 使用主窗口作为父级，而不是传入的master
        self.master = tk.Toplevel(master.winfo_toplevel())
        self.master.title("编辑患者")
        self.master.geometry("800x400")
        self.master.resizable(True, True)
        
        # 创建患者信息输入表单
        self.create_patient_form(patient_name, patient_gender, patient_age, patient_phone, patient_history)
    
    def create_patient_form(self, patient_name, patient_gender, patient_age, patient_phone, patient_history):
        """创建患者信息输入表单，填充现有信息"""
        form_frame = ttk.LabelFrame(self.master, text="患者信息")
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # 基本信息
        ttk.Label(form_frame, text="姓名:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(form_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, patient_name)  # 填充现有姓名
        
        ttk.Label(form_frame, text="性别:", font=("微软雅黑", 9, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.gender_entry = ttk.Combobox(form_frame, values=["男", "女"], width=5)
        self.gender_entry.grid(row=0, column=3, padx=5, pady=5)
        self.gender_entry.set(patient_gender)  # 填充现有性别
        
        ttk.Label(form_frame, text="年龄:", font=("微软雅黑", 9, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.age_entry = ttk.Entry(form_frame, width=8)
        self.age_entry.grid(row=0, column=5, padx=5, pady=5)
        self.age_entry.insert(0, patient_age)  # 填充现有年龄
        
        ttk.Label(form_frame, text="电话:", font=("微软雅黑", 9, "bold")).grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(form_frame, width=15)
        self.phone_entry.grid(row=0, column=7, padx=5, pady=5)
        self.phone_entry.insert(0, patient_phone)  # 填充现有电话
        
        # 病史
        ttk.Label(form_frame, text="病史:", font=("微软雅黑", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.history_text = tk.Text(form_frame, height=3, width=60)
        self.history_text.grid(row=1, column=1, columnspan=7, padx=5, pady=5)
        self.history_text.insert("1.0", patient_history or "")  # 填充现有病史
        
        # 操作按钮
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=8, pady=5)
        
        ttk.Button(btn_frame, text="保存", command=self.save_patient).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=self.master.destroy).pack(side="left", padx=5)
    
    def clear_form(self):
        """清空表单"""
        self.name_entry.delete(0, tk.END)
        self.gender_entry.current(0)
        self.age_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.history_text.delete("1.0", tk.END)

    def save_patient(self):
        """保存患者信息"""
        name = self.name_entry.get().strip()
        gender = self.gender_entry.get()
        age = self.age_entry.get()
        phone = self.phone_entry.get()
        history = self.history_text.get("1.0", "end").strip()

        # 必填项验证
        if not name:
            messagebox.showerror("错误", "姓名为必填项，请填写患者姓名")
            self.name_entry.focus_set()  # 将焦点设置到姓名输入框
            return
        
        if not phone:
            messagebox.showerror("错误", "电话为必填项，请填写患者电话")
            self.phone_entry.focus_set()  # 将焦点设置到电话输入框
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 更新患者信息
            cursor.execute("""
                UPDATE patients SET name = ?, gender = ?, age = ?, phone = ?, history = ?
                WHERE id = ?
            """, (name, gender, age, phone, history, self.patient_id))
            conn.commit()
            messagebox.showinfo("成功", "患者信息已更新")
            
            # 关闭窗口
            self.master.destroy()
            
            # 刷新父窗口的患者列表
            self.parent_window.load_patients()
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {str(e)}")
        finally:
            conn.close()
