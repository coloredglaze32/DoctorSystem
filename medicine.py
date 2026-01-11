# medicine.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class MedicineWindow:
    def __init__(self, master):
        self.master = master
        
        # 创建药品表单
        self.create_medicine_form()
        
        # 加载药品数据
        self.load_medicines()
    
    def create_medicine_form(self):
        """创建药品表单"""
        # 药品查询表单
        search_frame = ttk.LabelFrame(self.master, text="查询条件")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 药品名称查询
        ttk.Label(search_frame, text="药品名称:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_search = ttk.Entry(search_frame, width=15)
        self.name_search.grid(row=0, column=1, padx=5, pady=5)
        
        # 用法查询
        ttk.Label(search_frame, text="用法:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.usage_search = ttk.Entry(search_frame, width=15)
        self.usage_search.grid(row=0, column=3, padx=5, pady=5)
        
        # 查询按钮
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="查询", command=self.search_medicines).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_search).pack(side="left", padx=5)
        
        # 药品信息表单
        form_frame = ttk.LabelFrame(self.master, text="药品信息")
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # 药品名称
        ttk.Label(form_frame, text="药品名称:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 库存
        ttk.Label(form_frame, text="库存:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.stock_entry = ttk.Entry(form_frame, width=10)
        self.stock_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 单位
        ttk.Label(form_frame, text="单位:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.unit_entry = ttk.Combobox(form_frame, values=["包", "盒", "瓶", "克", "粒"], width=5)
        self.unit_entry.grid(row=0, column=5, padx=5, pady=5)
        self.unit_entry.current(0)
        
        # 用法
        ttk.Label(form_frame, text="用法:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.usage_entry = ttk.Entry(form_frame, width=25)
        self.usage_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        ttk.Button(btn_frame, text="保存", command=self.save_medicine).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_form).pack(side="left", padx=5)
    
    def load_medicines(self):
        """加载药品数据"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, stock, unit, usage FROM medicines")
        medicines = cursor.fetchall()
        conn.close()
        
        # 创建药品列表
        self.create_medicine_list(medicines)
    
    def create_medicine_list(self, medicines):
        """创建药品列表"""
        # 如果已有列表，先清空
        for widget in self.master.winfo_children():
            if widget != self.name_entry.master and widget != self.name_search.master:  # 保留表单部分
                widget.destroy()
        
        # 创建新列表
        list_frame = ttk.LabelFrame(self.master, text="药品列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ("id", "name", "stock", "unit", "usage", "modify", "delete")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        # 设置列标题（左对齐）
        column_titles = {"id": "ID", "name": "药品名称", "stock": "库存", "unit": "单位", "usage": "用法", "modify": "修改", "delete": "删除"}
        for col in columns:
            self.tree.heading(col, text=column_titles[col], anchor="w")
            if col == "id":
                self.tree.column(col, width=50)
            elif col == "name":
                self.tree.column(col, width=150)
            elif col == "usage":
                self.tree.column(col, width=100)
            elif col == "modify" or col == "delete":
                self.tree.column(col, width=60)
            else:
                self.tree.column(col, width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side="left", fill="both", expand=True)
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
        self.tree.bind("<Double-1>", self.on_medicine_selected)
        # 绑定点击事件
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        
        # 添加数据
        for index, medicine in enumerate(medicines):
            # 添加操作按钮的文本
            medicine_with_actions = medicine + ("修改", "删除")
            item_id = self.tree.insert("", "end", values=medicine_with_actions)
            # 根据行号设置交替颜色
            if index % 2 == 0:
                self.tree.item(item_id, tags=("evenrow",))
            else:
                self.tree.item(item_id, tags=("oddrow",))
        
        # 强制更新UI以确保样式生效
        self.master.update_idletasks()
    
    def save_medicine(self):
        """保存药品信息"""
        name = self.name_entry.get().strip()
        stock = self.stock_entry.get()
        unit = self.unit_entry.get()
        usage = self.usage_entry.get().strip()
        
        if not name:
            messagebox.showerror("错误", "请输入药品名称")
            return
        
        # 检查库存是否为数字
        if stock and not stock.isdigit():
            messagebox.showerror("错误", "库存必须是数字")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在同名药品
        cursor.execute("SELECT id FROM medicines WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新药品
            cursor.execute("""
                UPDATE medicines SET stock = ?, unit = ?, usage = ?
                WHERE id = ?
            """, (int(stock) if stock else 0, unit, usage, existing[0]))
            messagebox.showinfo("成功", "药品信息已更新")
        else:
            # 新增药品
            cursor.execute("""
                INSERT INTO medicines (name, stock, unit, usage)
                VALUES (?, ?, ?, ?)
            """, (name, int(stock) if stock else 0, unit, usage))
            messagebox.showinfo("成功", "药品信息已保存")
        
        conn.commit()
        conn.close()
        
        # 刷新列表
        self.load_medicines()
        self.clear_form()
    
    def clear_form(self):
        """清空表单"""
        self.name_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.unit_entry.current(0)
        self.usage_entry.delete(0, tk.END)
    
    def on_medicine_selected(self, event):
        """处理药品列表项双击事件"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        
        # 填充表单
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])  # values[1] 是药品名称
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, values[2])  # values[2] 是库存
        self.unit_entry.set(values[3])  # values[3] 是单位
        self.usage_entry.delete(0, tk.END)
        self.usage_entry.insert(0, values[4])  # values[4] 是用法
    
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
            medicine_id = values[0]
            medicine_name = values[1]
            medicine_stock = values[2]
            medicine_unit = values[3]
            medicine_usage = values[4]
            
            # 根据点击的列执行相应操作
            if col == "#6":  # 修改列
                self.open_edit_window(medicine_id, medicine_name, medicine_stock, medicine_unit, medicine_usage)
            elif col == "#7":  # 删除列
                self.delete_medicine(medicine_id)
    
    def open_edit_window(self, medicine_id, medicine_name, medicine_stock, medicine_unit, medicine_usage):
        """打开编辑窗口"""
        # 填充表单
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, medicine_name)
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, medicine_stock)
        self.unit_entry.set(medicine_unit)
        self.usage_entry.delete(0, tk.END)
        self.usage_entry.insert(0, medicine_usage)
        
        # 保存按钮功能会更新这个药品
        messagebox.showinfo("提示", f"请修改药品信息后点击保存按钮")
    
    def delete_medicine(self, medicine_id):
        """删除药品"""
        if messagebox.askyesno("确认", "确定要删除该药品吗？"):
            conn = get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
                conn.commit()
                messagebox.showinfo("成功", "药品已删除")
                # 重新加载药品列表
                self.load_medicines()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
            finally:
                conn.close()
    
    def search_medicines(self):
        """根据条件查询药品"""
        name = self.name_search.get().strip()
        usage = self.usage_search.get().strip()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        
        if usage:
            conditions.append("usage LIKE ?")
            params.append(f"%{usage}%")
        
        if conditions:
            query = f"SELECT id, name, stock, unit, usage FROM medicines WHERE {' AND '.join(conditions)}"
        else:
            query = "SELECT id, name, stock, unit, usage FROM medicines"
        
        cursor.execute(query, params)
        medicines = cursor.fetchall()
        conn.close()
        
        # 重新创建列表
        self.create_medicine_list(medicines)
    
    def reset_search(self):
        """重置查询条件"""
        self.name_search.delete(0, tk.END)
        self.usage_search.delete(0, tk.END)
        self.load_medicines()