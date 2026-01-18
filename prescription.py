# prescription.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class PrescriptionWindow:
    def __init__(self, master, record_id=None):
        self.master = master
        # 保存病历ID（如果从病历进入）
        self.record_id = record_id
        
        # 创建查询表单
        self.create_search_form()
        
        # 创建返回按钮
        self.create_back_button()
        
        # 创建处方列表
        self.create_prescription_list()
        
        # 加载处方数据
        self.load_prescription()
    
    def create_back_button(self):
        """创建返回按钮和收藏按钮"""
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="返回病历列表", command=self.back_to_records).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="收藏当前处方", command=self.add_to_favorites).pack(side="left", padx=5)
    
    def create_search_form(self):
        """创建查询表单"""
        search_frame = ttk.LabelFrame(self.master, text="查询条件")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 患者姓名查询
        ttk.Label(search_frame, text="患者姓名:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.patient_name_search = ttk.Entry(search_frame, width=15, font=("微软雅黑", 10))
        self.patient_name_search.grid(row=0, column=1, padx=5, pady=10)
        
        # 病历ID查询
        ttk.Label(search_frame, text="病历ID:", font=("微软雅黑", 10, "bold")).grid(row=0, column=2, padx=5, pady=10, sticky="e")
        self.record_id_search = ttk.Entry(search_frame, width=10, font=("微软雅黑", 10))
        self.record_id_search.grid(row=0, column=3, padx=5, pady=10)
        
        # 日期查询
        ttk.Label(search_frame, text="日期:", font=("微软雅黑", 10, "bold")).grid(row=0, column=4, padx=5, pady=10, sticky="e")
        self.date_search = ttk.Entry(search_frame, width=12, font=("微软雅黑", 10))
        self.date_search.grid(row=0, column=5, padx=5, pady=10)

        # 查询按钮
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=6, padx=5, pady=10)
        
        ttk.Button(btn_frame, text="查询", command=self.search_prescriptions).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_search).pack(side="left", padx=5)
    
    def create_prescription_list(self):
        """创建处方列表"""
        list_frame = ttk.LabelFrame(self.master, text="处方列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ("record_id", "patient_name", "date", "medicine", "dosage", "usage")
        self.prescription_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        self.prescription_tree.heading("record_id", text="病历ID", anchor="center")
        self.prescription_tree.column("record_id", width=80, anchor="center")
        self.prescription_tree.heading("patient_name", text="患者姓名", anchor="center")
        self.prescription_tree.column("patient_name", width=120, anchor="center")
        self.prescription_tree.heading("date", text="日期", anchor="center")
        self.prescription_tree.column("date", width=100, anchor="center")
        self.prescription_tree.heading("medicine", text="药品", anchor="center")
        self.prescription_tree.column("medicine", width=150, anchor="center")
        self.prescription_tree.heading("dosage", text="剂量", anchor="center")
        self.prescription_tree.column("dosage", width=80, anchor="center")
        self.prescription_tree.heading("usage", text="用法", anchor="center")
        self.prescription_tree.column("usage", width=120, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.prescription_tree.yview)
        self.prescription_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.prescription_tree.pack(side="left", fill="both", expand=True)
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
        
        # 绑定右键事件 - 复制行信息到剪贴板
        self.prescription_tree.bind("<Button-3>", self.copy_row_to_clipboard)

    def load_prescription(self):
        """加载处方数据"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 如果有特定病历ID，则只加载该病历的处方
        if self.record_id:
            cursor.execute("""
                SELECT p.record_id, p.medicine, p.dosage, p.usage, mr.date, pt.name
                FROM prescriptions p
                JOIN medical_records mr ON p.record_id = mr.id
                JOIN patients pt ON mr.patient_id = pt.id
                WHERE p.record_id = ?
                ORDER BY mr.date DESC
            """, (self.record_id,))
        else:
            cursor.execute("""
                SELECT p.record_id, p.medicine, p.dosage, p.usage, mr.date, pt.name
                FROM prescriptions p
                JOIN medical_records mr ON p.record_id = mr.id
                JOIN patients pt ON mr.patient_id = pt.id
                ORDER BY mr.date DESC
            """)
        
        prescriptions = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.prescription_tree.get_children():
            self.prescription_tree.delete(item)
        
        # 添加数据 - 注意顺序：record_id, patient_name, date, medicine, dosage, usage
        for pres in prescriptions:
            # 重新组织数据以匹配列标题顺序
            record_id = pres[0]
            medicine = pres[1]
            dosage = pres[2]
            usage = pres[3]
            date = pres[4]
            patient_name = pres[5]
            
            self.prescription_tree.insert("", "end", values=(record_id, patient_name, date, medicine, dosage, usage))
    
    def search_prescriptions(self):
        """根据条件查询处方"""
        patient_name = self.patient_name_search.get().strip()
        record_id = self.record_id_search.get().strip()
        date = self.date_search.get().strip()

        conn = get_connection()
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if patient_name:
            conditions.append("pt.name LIKE ?")
            params.append(f"%{patient_name}%")

        if record_id:
            conditions.append("p.record_id = ?")
            params.append(record_id)

        if date:
            conditions.append("mr.date = ?")
            params.append(date)

        query = """
            SELECT p.record_id, p.medicine, p.dosage, p.usage, mr.date, pt.name
            FROM prescriptions p
            JOIN medical_records mr ON p.record_id = mr.id
            JOIN patients pt ON mr.patient_id = pt.id
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY mr.date DESC"

        cursor.execute(query, params)
        prescriptions = cursor.fetchall()
        conn.close()
        
        # 清空现有数据
        for item in self.prescription_tree.get_children():
            self.prescription_tree.delete(item)
        
        # 添加查询结果 - 注意顺序：record_id, patient_name, date, medicine, dosage, usage
        for pres in prescriptions:
            # 重新组织数据以匹配列标题顺序
            record_id = pres[0]
            medicine = pres[1]
            dosage = pres[2]
            usage = pres[3]
            date = pres[4]
            patient_name = pres[5]
            
            self.prescription_tree.insert("", "end", values=(record_id, patient_name, date, medicine, dosage, usage))

    def reset_search(self):
        """重置查询条件"""
        self.patient_name_search.delete(0, tk.END)
        self.record_id_search.delete(0, tk.END)
        self.date_search.delete(0, tk.END)
        self.load_prescription()
    
    def copy_row_to_clipboard(self, event):
        """复制行信息到剪贴板"""
        # 选中点击的行
        item = self.prescription_tree.identify_row(event.y)
        if item:
            self.prescription_tree.selection_set(item)
            values = self.prescription_tree.item(item, "values")
            
            # 将行数据转换为字符串格式
            row_str = "\t".join([str(v) for v in values])
            self.master.clipboard_clear()  # 清空剪贴板
            self.master.clipboard_append(row_str)  # 添加到剪贴板
            messagebox.showinfo("提示", "已复制行信息到剪贴板")

    def add_to_favorites(self):
        """收藏当前病历的所有处方（收藏选中的那个病历的所有药品）"""
        # 获取当前选中的处方
        selected_items = self.prescription_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请选择要收藏的处方")
            return
        
        # 获取选中项的信息
        item_values = self.prescription_tree.item(selected_items[0], "values")
        record_id = item_values[0]  # 病历ID
        patient_name = item_values[1]
        selected_medicine = item_values[3]  # 选中的药品名称
        
        # 获取该病历的所有处方信息（不只是选中的那一个）
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.medicine, p.dosage, p.usage
            FROM prescriptions p
            WHERE p.record_id = ?
        """, (record_id,))
        prescriptions = cursor.fetchall()
        conn.close()
        
        if not prescriptions:
            messagebox.showwarning("警告", "未找到相关处方信息")
            return
        
        # 准备处方数据 - 包含该病历的所有处方
        prescription_data = {
            'record_id': record_id,
            'patient_name': patient_name,
            'prescriptions': []
        }
        
        for pres in prescriptions:
            prescription_data['prescriptions'].append({
                'medicine': pres[0],
                'dosage': pres[1],
                'usage': pres[2]
            })
        
        # 提示用户即将收藏整个病历的所有处方
        medicine_list = [pres[0] for pres in prescriptions]
        medicine_str = "、".join(medicine_list)
        if messagebox.askyesno("确认收藏", f"您选择了药品 '{selected_medicine}'，将收藏该病历的所有药品组合：\n{medicine_str}\n\n是否继续？"):
            # 打开收藏对话框
            from favorite import AddToFavoritesDialog
            dialog = AddToFavoritesDialog(self.master, record_id, patient_name, prescription_data)

    def back_to_records(self):
        """返回病历列表"""
        # 清空当前界面并返回病历列表
        for widget in self.master.winfo_children():
            widget.destroy()
        
        import medical_record
        medical_record_window = medical_record.MedicalRecordWindow(self.master)
