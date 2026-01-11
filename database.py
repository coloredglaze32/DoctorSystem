# database.py
import sqlite3
import os
from config import DB_FILE

def init_db():
    """初始化数据库，创建必要表"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 创建患者表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            phone TEXT,
            history TEXT
        )
        ''')
        
        # 创建病历表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            wang TEXT,        -- 望诊
            wen TEXT,         -- 闻诊
            wen2 TEXT,        -- 问诊
            qie TEXT,         -- 切诊
            diagnosis TEXT,
            treatment TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
        ''')
        
        # 创建处方表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            medicine TEXT NOT NULL,
            dosage TEXT,
            usage TEXT,
            FOREIGN KEY (record_id) REFERENCES medical_records(id)
        )
        ''')
        
        # 创建药品表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            unit TEXT DEFAULT '包',
            usage TEXT DEFAULT ''
        )
        ''')
        
        # 检查是否已有usage列，如果没有则添加
        try:
            cursor.execute("PRAGMA table_info(medicines)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'usage' not in columns:
                cursor.execute("ALTER TABLE medicines ADD COLUMN usage TEXT DEFAULT ''")
                print("已为medicines表添加usage列")
        except Exception as e:
            print(f"检查或添加usage列时出错: {e}")
        
        conn.commit()
        conn.close()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_FILE)