"""
在浙招生高校名单构建脚本

从历年录取数据中提取在浙江招生的高校名单，并整合到数据库
"""

import pandas as pd
import sqlite3
import os
import re
from datetime import datetime

folder = r'C:\Users\Lenovo\OneDrive\Info\填报志愿\data\历年录取信息'
db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'

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

def clean_school_name(name):
    """清理学校名称，移除括号内容"""
    if pd.isna(name):
        return ''
    name = str(name).strip()
    # 移除括号及其内容
    name = re.sub(r'[（\(【\[].*?[）\)\】\]]', '', name)
    return name.strip()

print(f"在浙招生高校名单构建 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

all_schools = {}
year_stats = {}

for filename, year, batch in files_info:
    filepath = os.path.join(folder, filename)

    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filepath, engine='openpyxl')
        else:
            df = pd.read_excel(filepath)

        # 清理列名
        df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]

        for _, row in df.iterrows():
            school_name = str(row['学校名称']).strip() if pd.notna(row['学校名称']) else ''
            if not school_name:
                continue

            clean_name = clean_school_name(school_name)

            # 记录学校
            if clean_name not in all_schools:
                all_schools[clean_name] = {
                    'name': clean_name,
                    'original_name': school_name,
                    'code': str(int(row['学校代号'])) if pd.notna(row['学校代号']) else '',
                    'first_year': year,
                    'latest_year': year,
                    'batches': set([batch]),
                    'total_records': 0
                }
            else:
                all_schools[clean_name]['first_year'] = min(all_schools[clean_name]['first_year'], year)
                all_schools[clean_name]['latest_year'] = max(all_schools[clean_name]['latest_year'], year)
                all_schools[clean_name]['batches'].add(batch)

            all_schools[clean_name]['total_records'] += 1

        count = len(df)
        year_stats[(year, batch)] = count
        print(f"  {year}年{batch}: {count}条记录")

    except Exception as e:
        print(f"  错误 {filename}: {e}")

print(f"\n共发现 {len(all_schools)} 所高校")

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建在浙招生高校表
cursor.execute('''
CREATE TABLE IF NOT EXISTS zhejiang_recruiting_schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    original_name TEXT,
    school_code TEXT,
    first_year INTEGER,
    latest_year INTEGER,
    batches TEXT,
    total_records INTEGER,
    is_985 INTEGER,
    is_211 INTEGER,
    is_double_first_class INTEGER,
    UNIQUE(school_name)
)
''')

# 插入数据
for name, data in all_schools.items():
    # 检查是否为985/211/双一流（通过模糊匹配schools表）
    cursor.execute('''
        SELECT is_985, is_211, is_double_first_class FROM schools
        WHERE name LIKE ? || '%'
        LIMIT 1
    ''', (name[:4],))
    result = cursor.fetchone()
    is_985 = result[0] if result else 0
    is_211 = result[1] if result else 0
    is_double_first_class = result[2] if result else 0

    cursor.execute('''
        INSERT OR REPLACE INTO zhejiang_recruiting_schools
        (school_name, original_name, school_code, first_year, latest_year, batches, total_records, is_985, is_211, is_double_first_class)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['original_name'],
        data['code'],
        data['first_year'],
        data['latest_year'],
        ','.join(data['batches']),
        data['total_records'],
        is_985 if is_985 else 0,
        is_211 if is_211 else 0,
        is_double_first_class if is_double_first_class else 0
    ))

conn.commit()

# 统计
cursor.execute('SELECT COUNT(*) FROM zhejiang_recruiting_schools')
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM zhejiang_recruiting_schools WHERE is_985 = 1")
count_985 = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM zhejiang_recruiting_schools WHERE is_211 = 1")
count_211 = cursor.fetchone()[0]

print(f"\n数据库更新完成!")
print(f"在浙招生高校: {total} 所")
print(f"  其中985工程: {count_985} 所")
print(f"  其中211工程: {count_211} 所")

# 显示样本
print("\n样本数据 (985高校):")
cursor.execute('''
    SELECT school_name, original_name, latest_year, total_records
    FROM zhejiang_recruiting_schools
    WHERE is_985 = 1
    ORDER BY total_records DESC
    LIMIT 15
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} ({row[2]}年, {row[3]}条记录)")

# 创建一个视图用于常见查询
cursor.execute('''
CREATE OR REPLACE VIEW zhejiang_top_schools AS
SELECT school_name, original_name, latest_year, total_records,
       CASE WHEN is_985 = 1 THEN '985' WHEN is_211 = 1 THEN '211' WHEN is_double_first_class = 1 THEN '双一流' ELSE '普通' END as level
FROM zhejiang_recruiting_schools
ORDER BY is_985 DESC, is_211 DESC, is_double_first_class DESC, total_records DESC
''')

conn.close()
print("\n完成!")
