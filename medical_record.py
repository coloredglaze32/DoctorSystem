# medical_record.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_connection

class MedicalRecordWindow:
    def __init__(self, master, patient_id=None):
        self.master = master
        # 保存患者ID（如果从患者列表进入）
        self.patient_id = patient_id
        
        # 创建查询表单
        self.create_search_form()
        
        # 创建按钮区域
        self.create_buttons()
        
        # 创建病历列表
        self.create_record_list()
        
        # 加载病历数据
        self.load_records()
    
    def create_buttons(self):
        """创建按钮区域"""
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="导出患者数据", command=self.export_patient_data).pack(side="left", padx=5)
    
    def create_search_form(self):
        """创建查询表单"""
        search_frame = ttk.LabelFrame(self.master, text="查询条件")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 姓名查询
        ttk.Label(search_frame, text="患者姓名:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_search = ttk.Entry(search_frame, width=15)
        self.name_search.grid(row=0, column=1, padx=5, pady=5)
        
        # 电话查询
        ttk.Label(search_frame, text="电话:", font=("微软雅黑", 9, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.phone_search = ttk.Entry(search_frame, width=15)
        self.phone_search.grid(row=0, column=3, padx=5, pady=5)
        
        # 日期查询
        ttk.Label(search_frame, text="日期:", font=("微软雅黑", 9, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.date_search = ttk.Entry(search_frame, width=12)
        self.date_search.grid(row=0, column=5, padx=5, pady=5)

        # 查询按钮
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=6, columnspan=2, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="查询", command=self.search_records).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_search).pack(side="left", padx=5)
    
    def create_record_list(self):
        """创建病历列表"""
        list_frame = ttk.LabelFrame(self.master, text="病历列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ("id", "patient_name", "date", "diagnosis", "treatment", "actions")
        self.record_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # 设置列标题（左对齐）
        self.record_tree.heading("id", text="病历ID", anchor="w")
        self.record_tree.column("id", width=80)
        self.record_tree.heading("patient_name", text="患者姓名", anchor="w")
        self.record_tree.column("patient_name", width=100)
        self.record_tree.heading("date", text="日期", anchor="w")
        self.record_tree.column("date", width=100)
        self.record_tree.heading("diagnosis", text="诊断", anchor="w")
        self.record_tree.column("diagnosis", width=150)
        self.record_tree.heading("treatment", text="治疗方案", anchor="w")
        self.record_tree.column("treatment", width=200)
        self.record_tree.heading("actions", text="操作", anchor="w")
        self.record_tree.column("actions", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.record_tree.yview)
        self.record_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.record_tree.pack(side="left", fill="both", expand=True)
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
        
        # 绑定双击事件
        self.record_tree.bind("<Double-1>", self.on_record_double_click)
        # 绑定右键事件 - 复制行信息到剪贴板
        self.record_tree.bind("<Button-3>", self.copy_row_to_clipboard)

    def load_records(self):
        """加载病历数据"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 如果有特定患者ID，则只加载该患者的病历
        if self.patient_id:
            cursor.execute("""
                SELECT mr.id, p.name, mr.date, mr.diagnosis, mr.treatment
                FROM medical_records mr
                JOIN patients p ON mr.patient_id = p.id
                WHERE mr.patient_id = ?
                ORDER BY mr.date DESC  -- 按时间降序排列
            """, (self.patient_id,))
        else:
            cursor.execute("""
                SELECT mr.id, p.name, mr.date, mr.diagnosis, mr.treatment
                FROM medical_records mr
                JOIN patients p ON mr.patient_id = p.id
                ORDER BY mr.date DESC  -- 按时间降序排列
            """)
        
        records = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        # 添加数据
        for index, record in enumerate(records):
            # 添加操作按钮的文本
            record_with_action = record + ("查看处方",)
            item_id = self.record_tree.insert("", "end", values=record_with_action)
            # 根据行号设置交替颜色
            if index % 2 == 0:
                self.record_tree.item(item_id, tags=("evenrow",))
            else:
                self.record_tree.item(item_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.master.update_idletasks()

    def search_records(self):
        """根据条件查询病历"""
        name = self.name_search.get().strip()
        phone = self.phone_search.get().strip()
        date = self.date_search.get().strip()

        conn = get_connection()
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if name:
            conditions.append("p.name LIKE ?")
            params.append(f"%{name}%")

        if phone:
            conditions.append("p.phone LIKE ?")
            params.append(f"%{phone}%")

        if date:
            conditions.append("mr.date = ?")
            params.append(date)

        query = """
            SELECT mr.id, p.name, mr.date, mr.diagnosis, mr.treatment
            FROM medical_records mr
            JOIN patients p ON mr.patient_id = p.id
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY mr.date DESC"  # 按时间降序排列

        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        # 添加查询结果
        for index, record in enumerate(records):
            # 添加操作按钮的文本
            record_with_action = record + ("查看处方",)
            item_id = self.record_tree.insert("", "end", values=record_with_action)
            # 根据行号设置交替颜色
            if index % 2 == 0:
                self.record_tree.item(item_id, tags=("evenrow",))
            else:
                self.record_tree.item(item_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.master.update_idletasks()

    def reset_search(self):
        """重置查询条件"""
        self.name_search.delete(0, tk.END)
        self.phone_search.delete(0, tk.END)
        self.date_search.delete(0, tk.END)
        self.load_records()

    def copy_row_to_clipboard(self, event):
        """复制行信息到剪贴板"""
        # 选中点击的行
        item = self.record_tree.identify_row(event.y)
        if item:
            self.record_tree.selection_set(item)
            values = self.record_tree.item(item, "values")
            
            # 将行数据转换为字符串格式
            row_str = "\t".join([str(v) for v in values])
            self.master.clipboard_clear()  # 清空剪贴板
            self.master.clipboard_append(row_str)  # 添加到剪贴板
            messagebox.showinfo("提示", "已复制行信息到剪贴板")

    def export_patient_data(self):
        """导出患者数据"""
        from tkinter import filedialog, messagebox, ttk
        from datetime import datetime
        import json
        
        # 创建选择格式的窗口
        format_window = tk.Toplevel()
        format_window.title("选择导出格式")
        format_window.geometry("400x200")
        format_window.transient()  # 设置为临时窗口
        format_window.grab_set()   # 模态窗口
        
        # 居中显示
        format_window.geometry(f"+{format_window.winfo_screenwidth()//2-200}+{format_window.winfo_screenheight()//2-100}")
        
        # 使用ttkbootstrap样式
        try:
            import ttkbootstrap as ttk
            from ttkbootstrap import Style
            
            # 创建主框架
            main_frame = ttk.Frame(format_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 标题标签
            title_label = ttk.Label(main_frame, text="请选择导出格式:", font=("微软雅黑", 12, "bold"))
            title_label.pack(pady=10)
            
            format_var = tk.StringVar(value="txt")
            format_combo = ttk.Combobox(main_frame, textvariable=format_var, values=["txt", "pdf", "json", "csv"], state="readonly", width=12, font=("微软雅黑", 10))
            format_combo.pack(pady=10)
            
            def confirm_export():
                format_choice = format_var.get()
                
                # 选择保存路径
                if format_choice == "txt":
                    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_txt(file_path)
                elif format_choice == "pdf":
                    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_pdf(file_path)
                elif format_choice == "json":
                    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_json(file_path)
                elif format_choice == "csv":
                    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_csv(file_path)
                
                format_window.destroy()
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=15)
            
            # 确认按钮
            confirm_btn = ttk.Button(button_frame, text="确定", command=confirm_export, bootstyle="success-outline")
            confirm_btn.pack(side="left", padx=5)
            
            # 取消按钮
            cancel_btn = ttk.Button(button_frame, text="取消", command=format_window.destroy, bootstyle="secondary-outline")
            cancel_btn.pack(side="left", padx=5)
            
            # 绑定回车键
            format_window.bind('<Return>', lambda e: confirm_export())
            format_window.bind('<Escape>', lambda e: format_window.destroy())
            
            # 设置焦点到下拉框
            format_combo.focus_set()
        except ImportError:
            # 如果没有ttkbootstrap，则使用标准tkinter
            ttk.Label(format_window, text="请选择导出格式:", font=("Arial", 12)).pack(pady=20)
            
            format_var = tk.StringVar(value="txt")
            format_combo = ttk.Combobox(format_window, textvariable=format_var, values=["txt", "pdf", "json", "csv"], state="readonly", width=10)
            format_combo.pack(pady=10)
            
            def confirm_export():
                format_choice = format_var.get()
                
                # 选择保存路径
                if format_choice == "txt":
                    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_txt(file_path)
                elif format_choice == "pdf":
                    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_pdf(file_path)
                elif format_choice == "json":
                    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_json(file_path)
                elif format_choice == "csv":
                    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
                    if file_path:
                        self.export_to_csv(file_path)
                
                format_window.destroy()
            
            # 确认按钮
            ttk.Button(format_window, text="确定", command=confirm_export).pack(pady=10)
            
            # 绑定回车键
            format_window.bind('<Return>', lambda e: confirm_export())
            format_window.bind('<Escape>', lambda e: format_window.destroy())
            
            # 设置焦点到下拉框
            format_combo.focus_set()

    def export_to_txt(self, file_path):
        """导出到TXT文件"""
        try:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                # 获取所有患者及其病历和处方
                conn = get_connection()
                cursor = conn.cursor()
                
                # 查询所有患者及病历信息
                query = """
                    SELECT p.id, p.name, p.gender, p.age, p.phone, p.history,
                           mr.id, mr.date, mr.wang, mr.wen, mr.wen2, mr.qie, mr.diagnosis, mr.treatment
                    FROM patients p
                    LEFT JOIN medical_records mr ON p.id = mr.patient_id
                    ORDER BY p.id, mr.date ASC  -- 按患者ID和病历时间升序排列
                """
                cursor.execute(query)
                results = cursor.fetchall()
                conn.close()
                
                # 按患者分组数据
                patient_records = {}
                for row in results:
                    patient_id = row[0]
                    if patient_id not in patient_records:
                        patient_records[patient_id] = {
                            'info': row[:6],  # 基本信息
                            'records': []
                        }
                    
                    if row[6] is not None:  # 如果有病历记录
                        # 获取该病历的处方
                        record_id = row[6]
                        prescriptions = self.get_prescriptions_for_record(record_id)
                        
                        patient_records[patient_id]['records'].append({
                            'record': row[6:],
                            'prescriptions': prescriptions
                        })
                
                # 写入文件
                for patient_id, data in patient_records.items():
                    patient_info = data['info']
                    records = data['records']
                    
                    f.write(f"患者ID: {patient_info[0]}\n")
                    f.write(f"姓名: {patient_info[1]}\n")
                    f.write(f"性别: {patient_info[2]}\n")
                    f.write(f"年龄: {patient_info[3]}\n")
                    f.write(f"电话: {patient_info[4]}\n")
                    f.write(f"病史: {patient_info[5] if patient_info[5] else '无'}\n")
                    f.write("-" * 50 + "\n")
                    
                    if records:
                        for record_data in records:
                            record = record_data['record']
                            prescriptions = record_data['prescriptions']
                            
                            f.write(f"  病历ID: {record[0]}\n")
                            f.write(f"  日期: {record[1]}\n")
                            f.write(f"  望诊: {record[2] if record[2] else '无'}\n")
                            f.write(f"  闻诊: {record[3] if record[3] else '无'}\n")
                            f.write(f"  问诊: {record[4] if record[4] else '无'}\n")
                            f.write(f"  切诊: {record[5] if record[5] else '无'}\n")
                            f.write(f"  诊断: {record[6] if record[6] else '无'}\n")
                            f.write(f"  治疗方案: {record[7] if record[7] else '无'}\n")
                            
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
                    
                    f.write("\n" + "="*60 + "\n\n")
                
            messagebox.showinfo("成功", f"数据已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_to_csv(self, file_path):
        """导出到CSV文件"""
        import csv
        try:
            # 获取所有患者及其病历和处方
            conn = get_connection()
            cursor = conn.cursor()
            
            # 查询所有患者及病历信息
            query = """
                SELECT p.id, p.name, p.gender, p.age, p.phone, p.history,
                       mr.id, mr.date, mr.wang, mr.wen, mr.wen2, mr.qie, mr.diagnosis, mr.treatment
                FROM patients p
                LEFT JOIN medical_records mr ON p.id = mr.patient_id
                ORDER BY p.id, mr.date ASC  -- 按患者ID和病历时间升序排列
            """
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            # 按患者分组数据
            patient_records = {}
            for row in results:
                patient_id = row[0]
                if patient_id not in patient_records:
                    patient_records[patient_id] = {
                        'id': row[0],
                        'name': row[1],
                        'gender': row[2],
                        'age': row[3],
                        'phone': row[4],
                        'history': row[5],
                        'records': []
                    }
                
                if row[6] is not None:  # 如果有病历记录
                    # 获取该病历的处方
                    record_id = row[6]
                    prescriptions = self.get_prescriptions_for_record(record_id)
                    
                    record_data = {
                        'id': row[6],
                        'date': row[7],
                        'wang': row[8],
                        'wen': row[9],
                        'wen2': row[10],
                        'qie': row[11],
                        'diagnosis': row[12],
                        'treatment': row[13],
                        'prescriptions': prescriptions
                    }
                    
                    patient_records[patient_id]['records'].append(record_data)
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入表头
                writer.writerow(['患者ID', '姓名', '性别', '年龄', '电话', '病史', '病历ID', '病历日期', '望诊', '闻诊', '问诊', '切诊', '诊断', '治疗方案', '药品', '剂量', '用法'])
                
                # 写入数据
                for patient_id, data in patient_records.items():
                    records = data['records']
                    
                    if records:
                        for record_data in records:
                            prescriptions = record_data['prescriptions']
                            
                            if prescriptions:
                                # 如果有处方，每张处方占一行
                                for pres in prescriptions:
                                    writer.writerow([
                                        data['id'], data['name'], data['gender'], 
                                        data['age'], data['phone'], data['history'],
                                        record_data['id'], record_data['date'], 
                                        record_data['wang'], record_data['wen'], 
                                        record_data['wen2'], record_data['qie'], 
                                        record_data['diagnosis'], record_data['treatment'],
                                        pres[0], pres[1], pres[2]
                                    ])
                            else:
                                # 如果没有处方，只写入病历信息
                                writer.writerow([
                                    data['id'], data['name'], data['gender'], 
                                    data['age'], data['phone'], data['history'],
                                    record_data['id'], record_data['date'], 
                                    record_data['wang'], record_data['wen'], 
                                    record_data['wen2'], record_data['qie'], 
                                    record_data['diagnosis'], record_data['treatment'],
                                    '', '', ''
                                ])
                    else:
                        # 如果没有病历，只写入患者基本信息
                        writer.writerow([
                            data['id'], data['name'], data['gender'], 
                            data['age'], data['phone'], data['history'],
                            '', '', '', '', '', '', '', '', '', '', ''
                        ])
                
            messagebox.showinfo("成功", f"数据已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def get_prescriptions_for_record(self, record_id):
        """获取指定病历的处方"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT medicine, dosage, usage
            FROM prescriptions
            WHERE record_id = ?
        """, (record_id,))
        prescriptions = cursor.fetchall()
        conn.close()
        return prescriptions

    def export_to_json(self, file_path):
        """导出到JSON文件"""
        import json
        try:
            # 获取所有患者及其病历和处方
            conn = get_connection()
            cursor = conn.cursor()
            
            # 查询所有患者及病历信息
            query = """
                SELECT p.id, p.name, p.gender, p.age, p.phone, p.history,
                       mr.id, mr.date, mr.wang, mr.wen, mr.wen2, mr.qie, mr.diagnosis, mr.treatment
                FROM patients p
                LEFT JOIN medical_records mr ON p.id = mr.patient_id
                ORDER BY p.id, mr.date ASC  -- 按患者ID和病历时间升序排列
            """
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            # 按患者分组数据
            patient_records = {}
            for row in results:
                patient_id = row[0]
                if patient_id not in patient_records:
                    patient_records[patient_id] = {
                        'id': row[0],
                        'name': row[1],
                        'gender': row[2],
                        'age': row[3],
                        'phone': row[4],
                        'history': row[5],
                        'records': []
                    }
                
                if row[6] is not None:  # 如果有病历记录
                    # 获取该病历的处方
                    record_id = row[6]
                    prescriptions = self.get_prescriptions_for_record(record_id)
                    
                    record_data = {
                        'id': row[6],
                        'date': row[7],
                        'wang': row[8],
                        'wen': row[9],
                        'wen2': row[10],
                        'qie': row[11],
                        'diagnosis': row[12],
                        'treatment': row[13],
                        'prescriptions': []
                    }
                    
                    for pres in prescriptions:
                        record_data['prescriptions'].append({
                            'medicine': pres[0],
                            'dosage': pres[1],
                            'usage': pres[2]
                        })
                    
                    patient_records[patient_id]['records'].append(record_data)
            
            # 写入JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(list(patient_records.values()), f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("成功", f"数据已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_to_pdf(self, file_path):
        """导出到PDF文件"""
        try:
            # 检查是否安装了reportlab
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
            except ImportError:
                messagebox.showerror("错误", "需要安装reportlab库来导出PDF文件:\npip install reportlab")
                return
            
            # 注册中文字体
            try:
                # 尝试使用系统字体
                pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                font_name = 'SimSun'
            except:
                try:
                    # 尝试使用其他常见中文字体
                    pdfmetrics.registerFont(TTFont('MSYH', 'msyh.ttc'))
                    font_name = 'MSYH'
                except:
                    # 如果找不到中文字体，尝试使用系统默认字体
                    font_name = 'Helvetica'
            
            # 获取所有患者及其病历和处方
            conn = get_connection()
            cursor = conn.cursor()
            
            # 查询所有患者及病历信息
            query = """
                SELECT p.id, p.name, p.gender, p.age, p.phone, p.history,
                       mr.id, mr.date, mr.wang, mr.wen, mr.wen2, mr.qie, mr.diagnosis, mr.treatment
                FROM patients p
                LEFT JOIN medical_records mr ON p.id = mr.patient_id
                ORDER BY p.id, mr.date ASC  -- 按患者ID和病历时间升序排列
            """
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            # 按患者分组数据
            patient_records = {}
            for row in results:
                patient_id = row[0]
                if patient_id not in patient_records:
                    patient_records[patient_id] = {
                        'id': row[0],
                        'name': row[1],
                        'gender': row[2],
                        'age': row[3],
                        'phone': row[4],
                        'history': row[5],
                        'records': []
                    }
                
                if row[6] is not None:  # 如果有病历记录
                    # 获取该病历的处方
                    record_id = row[6]
                    prescriptions = self.get_prescriptions_for_record(record_id)
                    
                    record_data = {
                        'id': row[6],
                        'date': row[7],
                        'wang': row[8],
                        'wen': row[9],
                        'wen2': row[10],
                        'qie': row[11],
                        'diagnosis': row[12],
                        'treatment': row[13],
                        'prescriptions': prescriptions
                    }
                    
                    patient_records[patient_id]['records'].append(record_data)
            
            # 创建PDF文档
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # 创建自定义样式以支持中文
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
                fontName=font_name
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=10,
                leading=14
            )
            
            # 添加标题
            title = Paragraph("中医诊所患者数据报告", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # 添加每个患者的信息
            for patient_id, data in patient_records.items():
                # 患者基本信息
                patient_info = f"""
                <b>患者ID:</b> {data['id']}<br/>
                <b>姓名:</b> {data['name']}<br/>
                <b>性别:</b> {data['gender']}<br/>
                <b>年龄:</b> {data['age']}<br/>
                <b>电话:</b> {data['phone']}<br/>
                <b>病史:</b> {data['history'] if data['history'] else '无'}<br/>
                """
                story.append(Paragraph(patient_info, normal_style))
                story.append(Spacer(1, 12))
                
                if data['records']:
                    for record_data in data['records']:
                        # 病历信息
                        record_info = f"""
                        <b>病历ID:</b> {record_data['id']}<br/>
                        <b>日期:</b> {record_data['date']}<br/>
                        <b>望诊:</b> {record_data['wang'] if record_data['wang'] else '无'}<br/>
                        <b>闻诊:</b> {record_data['wen'] if record_data['wen'] else '无'}<br/>
                        <b>问诊:</b> {record_data['wen2'] if record_data['wen2'] else '无'}<br/>
                        <b>切诊:</b> {record_data['qie'] if record_data['qie'] else '无'}<br/>
                        <b>诊断:</b> {record_data['diagnosis'] if record_data['diagnosis'] else '无'}<br/>
                        <b>治疗方案:</b> {record_data['treatment'] if record_data['treatment'] else '无'}<br/>
                        """
                        story.append(Paragraph(record_info, normal_style))
                        
                        # 处方信息
                        if record_data['prescriptions']:
                            story.append(Paragraph("<b>处方:</b>", normal_style))
                            data = [['药品', '剂量', '用法']]
                            for pres in record_data['prescriptions']:
                                data.append([pres[0], pres[1], pres[2]])
                            
                            # 设置表格样式以支持中文
                            table = Table(data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), font_name),
                                ('FONTNAME', (0, 1), (-1, -1), font_name),
                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                ('FONTSIZE', (0, 1), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            story.append(table)
                        else:
                            story.append(Paragraph("处方: 无", normal_style))
                        
                        story.append(Spacer(1, 12))
                else:
                    story.append(Paragraph("病历: 无", normal_style))
                
                story.append(Spacer(1, 20))
            
            # 构建PDF
            doc.build(story)
            messagebox.showinfo("成功", f"数据已导出到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def on_record_double_click(self, event):
        """处理病历列表项双击事件"""
        selection = self.record_tree.selection()
        if selection:
            item = selection[0]
            values = self.record_tree.item(item, "values")
            
            record_id = values[0]  # ID列的索引是0
            
            # 直接跳转到处方界面
            self.open_prescription_window(record_id)

    def on_right_click_record(self, event):
        """处理病历列表右键点击事件"""
        # 选中点击的行
        item = self.record_tree.identify_row(event.y)
        if item:
            self.record_tree.selection_set(item)
            values = self.record_tree.item(item, "values")
            
            # 检查操作列的值
            action_text = values[5]  # 操作列的索引是5
            record_id = values[0]  # ID列的索引是0
            
            if action_text == "查看处方":
                # 打开处方界面
                self.open_prescription_window(record_id)
                return

    def open_prescription_window(self, record_id):
        """打开处方窗口"""
        # 清空当前界面并显示处方界面
        for widget in self.master.winfo_children():
            widget.destroy()
        
        import prescription
        prescription_window = prescription.PrescriptionWindow(self.master, record_id=record_id)