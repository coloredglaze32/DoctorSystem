# favorite.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
from database import get_connection

class FavoriteManagementWindow:
    def __init__(self, master):
        self.master = master
        # 创建收藏夹管理界面
        self.create_folder_management()
        self.create_favorite_list()

    def create_folder_management(self):
        """创建收藏夹管理区域"""
        folder_frame = ttk.LabelFrame(self.master, text="收藏夹管理")
        folder_frame.pack(fill="x", padx=10, pady=5)

        # 创建新收藏夹
        ttk.Label(folder_frame, text="收藏夹名称:").pack(side="left", padx=5)
        self.folder_name_entry = ttk.Entry(folder_frame, width=20)
        self.folder_name_entry.pack(side="left", padx=5)
        ttk.Button(folder_frame, text="新建收藏夹", command=self.create_folder).pack(side="left", padx=5)
        ttk.Button(folder_frame, text="删除收藏夹", command=self.delete_folder).pack(side="left", padx=5)

        # 收藏夹列表
        folders_list_frame = ttk.LabelFrame(self.master, text="收藏夹列表")
        folders_list_frame.pack(fill="x", padx=10, pady=5)

        # 创建树形视图显示收藏夹
        columns = ("id", "name", "count", "created_time")
        self.folder_tree = ttk.Treeview(folders_list_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.folder_tree.heading("id", text="ID", anchor="w")
        self.folder_tree.column("id", width=50)
        self.folder_tree.heading("name", text="收藏夹名称", anchor="w")
        self.folder_tree.column("name", width=150)
        self.folder_tree.heading("count", text="处方数量", anchor="w")
        self.folder_tree.column("count", width=80)
        self.folder_tree.heading("created_time", text="创建时间", anchor="w")
        self.folder_tree.column("created_time", width=150)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(folders_list_frame, orient="vertical", command=self.folder_tree.yview)
        self.folder_tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.folder_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定双击事件
        self.folder_tree.bind("<Double-1>", self.on_folder_double_click)

        # 加载收藏夹列表
        self.load_folders()

    def create_favorite_list(self):
        """创建收藏处方列表"""
        favorite_frame = ttk.LabelFrame(self.master, text="收藏处方列表")
        favorite_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 创建树形视图显示收藏的处方
        columns = ("id", "folder_name", "patient_name", "prescription_details", "created_time", "actions")
        self.favorite_tree = ttk.Treeview(favorite_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.favorite_tree.heading("id", text="ID", anchor="w")
        self.favorite_tree.column("id", width=50)
        self.favorite_tree.heading("folder_name", text="收藏夹", anchor="w")
        self.favorite_tree.column("folder_name", width=100)
        self.favorite_tree.heading("patient_name", text="患者姓名", anchor="w")
        self.favorite_tree.column("patient_name", width=100)
        self.favorite_tree.heading("prescription_details", text="处方详情", anchor="w")
        self.favorite_tree.column("prescription_details", width=300)
        self.favorite_tree.heading("created_time", text="收藏时间", anchor="w")
        self.favorite_tree.column("created_time", width=150)
        self.favorite_tree.heading("actions", text="操作", anchor="w")
        self.favorite_tree.column("actions", width=80)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(favorite_frame, orient="vertical", command=self.favorite_tree.yview)
        self.favorite_tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.favorite_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 加载收藏处方列表
        self.load_favorites()

    def create_folder(self):
        """创建新收藏夹"""
        folder_name = self.folder_name_entry.get().strip()
        if not folder_name:
            messagebox.showerror("错误", "请输入收藏夹名称")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO favorite_folders (name) VALUES (?)", (folder_name,))
            conn.commit()
            messagebox.showinfo("成功", "收藏夹创建成功")
            self.folder_name_entry.delete(0, tk.END)
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
                self.load_folders()
                self.load_favorites()
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
            self.folder_tree.insert("", "end", values=folder)

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
            self.load_favorites_by_folder(folder_id)

    def load_favorites_by_folder(self, folder_id):
        """根据收藏夹ID加载收藏处方"""
        # 清空现有数据
        for item in self.favorite_tree.get_children():
            self.favorite_tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fp.id, ff.name, fp.patient_name, fp.prescription_data, fp.created_time
            FROM favorite_prescriptions fp
            LEFT JOIN favorite_folders ff ON fp.folder_id = ff.id
            WHERE fp.folder_id = ?
            ORDER BY fp.created_time DESC
        """, (folder_id,))
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