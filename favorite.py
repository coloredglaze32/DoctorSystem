# favorite.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
from database import get_connection

class FavoriteManagementWindow:
    def __init__(self, master):
        self.master = master
        # 当前显示状态：'folders'表示显示收藏夹列表，'favorites'表示显示某个收藏夹下的处方
        self.current_view = 'folders'
        # 当前选中的收藏夹ID
        self.current_folder_id = None
        # 创建收藏夹管理界面
        self.create_main_interface()

    def create_main_interface(self):
        """创建主要界面"""
        # 创建查询表单
        search_frame = ttk.LabelFrame(self.master, text="查询条件")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # 收藏夹名称查询
        ttk.Label(search_frame, text="收藏夹名称:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.folder_name_search = ttk.Entry(search_frame, width=15, font=("微软雅黑", 10))
        self.folder_name_search.grid(row=0, column=1, padx=5, pady=10)
        
        # 查询按钮
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=0, column=2, padx=5, pady=10)
        
        ttk.Button(btn_frame, text="查询", command=self.search_favorites).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset_search).pack(side="left", padx=5)
        
        # 按钮区域
        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # 返回按钮（初始隐藏）
        self.return_button = ttk.Button(button_frame, text="← 返回收藏夹列表", command=self.show_folders_view)
        self.return_button.pack(side="left", padx=5)
        self.return_button.pack_forget()  # 初始隐藏
        
        # 创建新收藏夹按钮
        ttk.Button(button_frame, text="新建收藏夹", command=self.show_create_folder_dialog).pack(side="left", padx=5)

        # 主内容区域
        self.main_content_frame = ttk.Frame(self.master)
        self.main_content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建收藏夹列表视图
        self.create_folders_view()
        
        # 创建收藏处方列表视图（初始隐藏）
        self.create_favorites_view()
        
        # 初始显示收藏夹列表
        self.show_folders_view()

    def create_folders_view(self):
        """创建收藏夹列表视图"""
        self.folders_frame = ttk.LabelFrame(self.main_content_frame, text="收藏夹列表")
        self.folders_frame.pack(fill="both", expand=True)
        
        # 创建树形视图显示收藏夹
        columns = ("id", "name", "count", "created_time", "actions")
        self.folder_tree = ttk.Treeview(self.folders_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题（居中对齐）
        self.folder_tree.heading("id", text="ID", anchor="center")
        self.folder_tree.column("id", width=50, anchor="center")
        self.folder_tree.heading("name", text="收藏夹名称", anchor="center")
        self.folder_tree.column("name", width=200, anchor="center")
        self.folder_tree.heading("count", text="处方数量", anchor="center")
        self.folder_tree.column("count", width=100, anchor="center")
        self.folder_tree.heading("created_time", text="创建时间", anchor="center")
        self.folder_tree.column("created_time", width=180, anchor="center")
        self.folder_tree.heading("actions", text="操作", anchor="center")
        self.folder_tree.column("actions", width=80, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.folders_frame, orient="vertical", command=self.folder_tree.yview)
        self.folder_tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.folder_tree.pack(side="left", fill="both", expand=True)
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
        
        # 绑定点击事件以处理删除操作
        self.folder_tree.bind("<ButtonRelease-1>", self.on_folder_tree_click)
        # 绑定双击事件
        self.folder_tree.bind("<Double-1>", self.on_folder_double_click)

        # 加载收藏夹列表
        self.load_folders()

    def create_favorites_view(self):
        """创建收藏处方列表视图"""
        self.favorites_frame = ttk.LabelFrame(self.main_content_frame, text="收藏夹处方列表")
        # 初始隐藏
        # self.favorites_frame.pack(fill="both", expand=True)
        
        # 创建树形视图显示收藏的处方
        columns = ("id", "patient_name", "prescription_details", "created_time", "actions")
        self.favorite_tree = ttk.Treeview(self.favorites_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题（居中对齐）
        self.favorite_tree.heading("id", text="ID", anchor="center")
        self.favorite_tree.column("id", width=50, anchor="center")
        self.favorite_tree.heading("patient_name", text="患者姓名", anchor="center")
        self.favorite_tree.column("patient_name", width=120, anchor="center")
        self.favorite_tree.heading("prescription_details", text="处方详情", anchor="center")
        self.favorite_tree.column("prescription_details", width=450, anchor="center")
        self.favorite_tree.heading("created_time", text="收藏时间", anchor="center")
        self.favorite_tree.column("created_time", width=150, anchor="center")
        self.favorite_tree.heading("actions", text="操作", anchor="center")
        self.favorite_tree.column("actions", width=80, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.favorites_frame, orient="vertical", command=self.favorite_tree.yview)
        self.favorite_tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.favorite_tree.pack(side="left", fill="both", expand=True)
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
        
        # 绑定事件处理删除操作
        self.favorite_tree.bind("<ButtonRelease-1>", self.on_favorite_tree_click)

    def show_folders_view(self):
        """显示收藏夹列表视图"""
        self.current_view = 'folders'
        # 隐藏处方列表视图
        self.favorites_frame.pack_forget()
        # 显示收藏夹列表视图
        self.folders_frame.pack(fill="both", expand=True)
        # 隐藏返回按钮
        self.return_button.pack_forget()
        # 重新加载收藏夹列表
        self.load_folders()

    def show_favorites_view(self, folder_id, folder_name):
        """显示收藏处方列表视图"""
        self.current_view = 'favorites'
        self.current_folder_id = folder_id
        # 隐藏收藏夹列表视图
        self.folders_frame.pack_forget()
        # 更新标题
        self.favorites_frame.config(text=f"'{folder_name}' 收藏夹处方列表")
        # 显示处方列表视图
        self.favorites_frame.pack(fill="both", expand=True)
        # 显示返回按钮
        self.return_button.pack(side="left", padx=5)
        # 加载该收藏夹下的处方
        self.load_favorites_by_folder(folder_id)

    def show_create_folder_dialog(self):
        """显示创建收藏夹对话框"""
        # 创建一个临时的对话框用于输入新收藏夹名称
        dialog = tk.Toplevel(self.master)
        dialog.title("新建收藏夹")
        dialog.geometry("300x100")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="收藏夹名称:").pack(pady=10)
        entry = ttk.Entry(dialog, width=20)
        entry.pack(pady=5)
        
        def save_folder():
            folder_name = entry.get().strip()
            if not folder_name:
                messagebox.showwarning("警告", "请输入收藏夹名称")
                return
            
            self.create_folder_with_name(folder_name)
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="确定", command=save_folder).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def create_folder_with_name(self, folder_name):
        """创建新收藏夹（内部方法）"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO favorite_folders (name) VALUES (?)", (folder_name,))
            conn.commit()
            messagebox.showinfo("成功", "收藏夹创建成功")
            self.load_folders()
        except Exception as e:
            messagebox.showerror("错误", f"创建收藏夹失败: {str(e)}")
        finally:
            conn.close()

    def delete_folder(self):
        """删除选中的收藏夹"""
        selection = self.folder_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的收藏夹")
            return

        item = selection[0]
        folder_id = self.folder_tree.item(item, "values")[0]

        if messagebox.askyesno("确认", "确定要删除该收藏夹吗？此操作不可恢复！"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # 先删除该收藏夹下的所有收藏处方
                cursor.execute("DELETE FROM favorite_prescriptions WHERE folder_id = ?", (folder_id,))
                # 再删除收藏夹
                cursor.execute("DELETE FROM favorite_folders WHERE id = ?", (folder_id,))
                conn.commit()
                messagebox.showinfo("成功", "收藏夹删除成功")
                # 根据当前视图决定刷新哪个列表
                if self.current_view == 'folders':
                    self.load_folders()
                else:
                    self.show_folders_view()  # 如果在查看某个收藏夹内容，返回列表
            except Exception as e:
                messagebox.showerror("错误", f"删除收藏夹失败: {str(e)}")
            finally:
                conn.close()

    def load_folders(self):
        """加载收藏夹列表"""
        # 清空现有数据
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, f.name, COUNT(fp.id) as prescription_count, f.created_time
            FROM favorite_folders f
            LEFT JOIN favorite_prescriptions fp ON f.id = fp.folder_id
            GROUP BY f.id, f.name, f.created_time
        """)
        folders = cursor.fetchall()
        conn.close()

        for folder in folders:
            # 添加操作列
            values = (folder[0], folder[1], folder[2], folder[3], "删除")
            self.folder_tree.insert("", "end", values=values)

    def on_folder_tree_click(self, event):
        """处理收藏夹列表中的点击事件"""
        region = self.folder_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.folder_tree.identify_row(event.y)
            column = self.folder_tree.identify_column(event.x)
            if column == "#5":  # 操作列
                self.delete_folder_by_id(item)

    def delete_folder_by_id(self, item):
        """根据ID删除收藏夹"""
        folder_id = self.folder_tree.item(item, "values")[0]

        if messagebox.askyesno("确认", "确定要删除该收藏夹吗？此操作不可恢复！"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # 先删除该收藏夹下的所有收藏处方
                cursor.execute("DELETE FROM favorite_prescriptions WHERE folder_id = ?", (folder_id,))
                # 再删除收藏夹
                cursor.execute("DELETE FROM favorite_folders WHERE id = ?", (folder_id,))
                conn.commit()
                messagebox.showinfo("成功", "收藏夹删除成功")
                # 根据当前视图决定刷新哪个列表
                if self.current_view == 'folders':
                    self.load_folders()
                else:
                    self.show_folders_view()  # 如果在查看某个收藏夹内容，返回列表
            except Exception as e:
                messagebox.showerror("错误", f"删除收藏夹失败: {str(e)}")
            finally:
                conn.close()

    def load_favorites(self):
        """加载收藏处方列表"""
        # 清空现有数据
        for item in self.favorite_tree.get_children():
            self.favorite_tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fp.id, ff.name, fp.patient_name, fp.prescription_data, fp.created_time
            FROM favorite_prescriptions fp
            LEFT JOIN favorite_folders ff ON fp.folder_id = ff.id
            ORDER BY fp.created_time DESC
        """)
        favorites = cursor.fetchall()
        conn.close()

        for fav in favorites:
            id, folder_name, patient_name, prescription_data, created_time = fav
            # 解析处方数据
            try:
                prescription_info = json.loads(prescription_data) if prescription_data else {}
                details = self.format_prescription_details(prescription_info)
            except:
                details = "处方数据解析失败"
            
            # 添加操作列
            values = (id, folder_name or "未分类", patient_name or "未知", details, created_time, "删除")
            item_id = self.favorite_tree.insert("", "end", values=values)

    def format_prescription_details(self, prescription_info):
        """格式化处方详情"""
        if not prescription_info:
            return "无处方信息"
        
        details = []
        prescriptions = prescription_info.get('prescriptions', [])
        for pres in prescriptions:
            medicine = pres.get('medicine', '')
            dosage = pres.get('dosage', '')
            usage = pres.get('usage', '')
            details.append(f"{medicine}({dosage})-{usage}")
        
        return "; ".join(details[:3]) + ("..." if len(details) > 3 else "")

    def on_folder_double_click(self, event):
        """双击收藏夹查看该收藏夹下的处方"""
        selection = self.folder_tree.selection()
        if selection:
            item = selection[0]
            folder_id = self.folder_tree.item(item, "values")[0]
            folder_name = self.folder_tree.item(item, "values")[1]
            self.show_favorites_view(folder_id, folder_name)

    def load_favorites_by_folder(self, folder_id):
        """根据收藏夹ID加载收藏处方"""
        # 清空现有数据
        for item in self.favorite_tree.get_children():
            self.favorite_tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fp.id, fp.patient_name, fp.prescription_data, fp.created_time
            FROM favorite_prescriptions fp
            WHERE fp.folder_id = ?
            ORDER BY fp.created_time DESC
        """, (folder_id,))
        favorites = cursor.fetchall()
        conn.close()

        for fav in favorites:
            id, patient_name, prescription_data, created_time = fav
            # 解析处方数据
            try:
                prescription_info = json.loads(prescription_data) if prescription_data else {}
                details = self.format_prescription_details(prescription_info)
            except:
                details = "处方数据解析失败"
            
            # 添加操作列
            values = (id, patient_name or "未知", details, created_time, "删除")
            item_id = self.favorite_tree.insert("", "end", values=values)

    def delete_favorite(self, item):
        """删除选中的收藏处方"""
        fav_id = self.favorite_tree.item(item, "values")[0]

        if messagebox.askyesno("确认", "确定要删除该收藏处方吗？此操作不可恢复！"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM favorite_prescriptions WHERE id = ?", (fav_id,))
                conn.commit()
                messagebox.showinfo("成功", "收藏处方删除成功")
                # 刷新当前视图
                if self.current_view == 'favorites' and self.current_folder_id:
                    self.load_favorites_by_folder(self.current_folder_id)
                elif self.current_view == 'folders':
                    self.load_folders()  # 如果在收藏夹列表页，也要刷新数量
            except Exception as e:
                messagebox.showerror("错误", f"删除收藏处方失败: {str(e)}")
            finally:
                conn.close()

    def on_favorite_tree_click(self, event):
        """处理收藏处方列表中的点击事件"""
        region = self.favorite_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.favorite_tree.identify_row(event.y)
            column = self.favorite_tree.identify_column(event.x)
            if column == "#5":  # 操作列 - 在收藏夹详情页面中操作列是第5列，不是第6列
                self.delete_favorite(item)

    def search_favorites(self):
        """根据收藏夹名称搜索收藏夹"""
        folder_name = self.folder_name_search.get().strip()

        # 清空现有数据
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT f.id, f.name, COUNT(fp.id) as prescription_count, f.created_time
            FROM favorite_folders f
            LEFT JOIN favorite_prescriptions fp ON f.id = fp.folder_id
            WHERE 1=1
        """
        params = []

        if folder_name:
            query += " AND f.name LIKE ?"
            params.append(f"%{folder_name}%")

        query += " GROUP BY f.id, f.name, f.created_time ORDER BY f.created_time DESC"

        cursor.execute(query, params)
        folders = cursor.fetchall()
        conn.close()

        for folder in folders:
            # 添加操作列
            values = (folder[0], folder[1], folder[2], folder[3], "删除")
            self.folder_tree.insert("", "end", values=values)

    def reset_search(self):
        """重置查询条件"""
        self.folder_name_search.delete(0, tk.END)
        # 重置查询时返回收藏夹列表视图
        if self.current_view == 'favorites':
            self.show_folders_view()
        else:
            self.load_folders()


class AddToFavoritesDialog:
    """添加到收藏夹对话框"""
    def __init__(self, parent, record_id, patient_name, prescription_data):
        self.parent = parent
        self.record_id = record_id
        self.patient_name = patient_name
        self.prescription_data = prescription_data
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("收藏处方")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()  # 模态窗口
        
        # 居中显示
        self.center_window()
        
        self.create_widgets()

    def center_window(self):
        """居中显示窗口"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 选择收藏夹
        folder_frame = ttk.LabelFrame(self.dialog, text="选择收藏夹")
        folder_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 收藏夹选择下拉框
        ttk.Label(folder_frame, text="收藏夹:").pack(anchor="w", padx=5, pady=5)
        
        # 获取所有收藏夹
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM favorite_folders")
        folders = cursor.fetchall()
        conn.close()

        folder_options = [("新建收藏夹", -1)]  # 添加新建选项
        for fid, name in folders:
            folder_options.append((name, fid))

        self.selected_folder = tk.StringVar()
        if folder_options:
            self.selected_folder.set(folder_options[0][0])  # 默认选择第一项
        else:
            self.selected_folder.set("新建收藏夹")

        self.folder_combo = ttk.Combobox(
            folder_frame, 
            textvariable=self.selected_folder,
            values=[option[0] for option in folder_options],
            state="readonly"
        )
        self.folder_combo.pack(fill="x", padx=5, pady=5)

        # 新收藏夹输入框（当选择"新建收藏夹"时显示）
        new_folder_frame = ttk.Frame(folder_frame)
        new_folder_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(new_folder_frame, text="新收藏夹名称:").pack(anchor="w")
        self.new_folder_entry = ttk.Entry(new_folder_frame)
        self.new_folder_entry.pack(fill="x", pady=2)
        self.new_folder_entry.pack_forget()  # 默认隐藏

        # 绑定下拉框变化事件
        self.folder_combo.bind("<<ComboboxSelected>>", self.on_folder_selected)

        # 按钮框架
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="收藏", command=self.add_to_favorites).pack(side="left", padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side="left", padx=5)

    def on_folder_selected(self, event):
        """当选择收藏夹时的处理"""
        if self.selected_folder.get() == "新建收藏夹":
            self.new_folder_entry.pack(fill="x", pady=2)
        else:
            self.new_folder_entry.pack_forget()

    def add_to_favorites(self):
        """添加到收藏夹"""
        selected_text = self.selected_folder.get()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取或创建收藏夹ID
            folder_id = None
            if selected_text == "新建收藏夹":
                new_folder_name = self.new_folder_entry.get().strip()
                if not new_folder_name:
                    messagebox.showerror("错误", "请输入新收藏夹名称")
                    return
                
                # 检查收藏夹是否已存在
                cursor.execute("SELECT id FROM favorite_folders WHERE name = ?", (new_folder_name,))
                existing = cursor.fetchone()
                if existing:
                    messagebox.showerror("错误", "该收藏夹名称已存在")
                    return
                
                # 创建新收藏夹
                cursor.execute("INSERT INTO favorite_folders (name) VALUES (?)", (new_folder_name,))
                folder_id = cursor.lastrowid
            else:
                # 查找现有收藏夹ID
                cursor.execute("SELECT id FROM favorite_folders WHERE name = ?", (selected_text,))
                result = cursor.fetchone()
                if result:
                    folder_id = result[0]
                else:
                    messagebox.showerror("错误", "找不到指定的收藏夹")
                    return

            # 添加收藏处方
            prescription_json = json.dumps(self.prescription_data, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO favorite_prescriptions (folder_id, record_id, patient_name, prescription_data)
                VALUES (?, ?, ?, ?)
            """, (folder_id, self.record_id, self.patient_name, prescription_json))
            
            conn.commit()
            messagebox.showinfo("成功", "处方已收藏")
            self.dialog.destroy()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("错误", f"收藏失败: {str(e)}")
        finally:
            conn.close()