import pandas as pd
import sqlite3
import os
import re

# 文件夹路径
folder = r"C:\Users\Lenovo\OneDrive\Info\填报志愿\data\历年录取信息"
db_file = r"C:\Users\Lenovo\OneDrive\Desktop\projects\zhejiangzhiyuan\universities.db"

# 文件列表和年份/批次信息
files_info = [
    ('2021普通一段.xls', 2021, '一段'),
    ('2021普通二段.xlsx', 2021, '二段'),
    ('2022普通一段.xls', 2022, '一段'),
    ('2022普通二段.xls', 2022, '二段'),
    ('2023普通一段.xls', 2023, '一段'),
    ('2023普通二段.xls', 2023, '二段'),
    ('2024普通一段.xls', 2024, '一段'),
    ('2024普通二段.xls', 2024, '二段'),
    ('2025普通一段.xlsx', 2025, '一段'),
    ('2025普通二段.xls', 2025, '二段'),
]

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建录取信息表
cursor.execute('''
CREATE TABLE IF NOT EXISTS admission_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    batch TEXT NOT NULL,
    school_code TEXT,
    school_name TEXT NOT NULL,
    major_code TEXT,
    major_name TEXT NOT NULL,
    enrollment_plan INTEGER,
    score_line INTEGER,
    rank_position REAL
)
''')

# 提取年份函数
def extract_year(filename):
    match = re.search(r'(\d{4})', filename)
    return int(match.group(1)) if match else None

# 提取批次函数
def extract_batch(filename):
    if '一段' in filename:
        return '一段'
    elif '二段' in filename:
        return '二段'
    elif '三段' in filename:
        return '三段'
    return ''

# 提取所有数据
total_records = 0
year_stats = {}

for filename, year, batch in files_info:
    filepath = os.path.join(folder, filename)

    # 读取文件
    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filepath, engine='openpyxl')
        else:
            df = pd.read_excel(filepath)

        # 清理列名中的空格
        df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]

        # 确保必要的列存在
        required_cols = ['学校代号', '学校名称', '专业代号', '专业名称', '计划数', '分数线', '位次']
        if not all(col in df.columns for col in required_cols):
            print(f"跳过 {filename} - 缺少必要列")
            continue

        # 插入数据
        for _, row in df.iterrows():
            # 处理NaN值
            school_code = str(int(row['学校代号'])) if pd.notna(row['学校代号']) else ''
            school_name = str(row['学校名称']).strip() if pd.notna(row['学校名称']) else ''
            major_code = str(int(row['专业代号'])) if pd.notna(row['专业代号']) else ''
            major_name = str(row['专业名称']).strip() if pd.notna(row['专业名称']) else ''
            enrollment_plan = int(row['计划数']) if pd.notna(row['计划数']) else 0
            score_line = int(row['分数线']) if pd.notna(row['分数线']) else 0
            rank_position = float(row['位次']) if pd.notna(row['位次']) else None

            cursor.execute('''
                INSERT INTO admission_records (year, batch, school_code, school_name, major_code, major_name, enrollment_plan, score_line, rank_position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (year, batch, school_code, school_name, major_code, major_name, enrollment_plan, score_line, rank_position))

        count = len(df)
        total_records += count
        year_stats[(year, batch)] = count
        print(f"已处理 {filename}: {count} 条记录")

    except Exception as e:
        print(f"错误 {filename}: {e}")

conn.commit()

# 统计
cursor.execute("SELECT COUNT(*) FROM admission_records")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT year) FROM admission_records")
year_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT school_name) FROM admission_records")
school_count = cursor.fetchone()[0]

print(f"\n数据库更新完成!")
print(f"总记录数: {total}")
print(f"涉及年份: {year_count} 年")
print(f"涉及高校: {school_count}")

# 按年份统计
print("\n各年份记录数:")
for (year, batch), count in sorted(year_stats.items()):
    print(f"  {year}年 {batch}: {count}")

conn.close()
print(f"\n数据库已更新: {db_file}")
