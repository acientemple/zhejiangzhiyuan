"""
将整合后的高校数据存入数据库
"""

import sqlite3
import pandas as pd
import re
from datetime import datetime

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'

print(f"保存整合数据到数据库 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# 1. 创建整合高校信息表
print("\n[1] 创建 integrated_schools 表...")
cur.execute('''
CREATE TABLE IF NOT EXISTS integrated_schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    latest_year INTEGER,
    major_count INTEGER,
    record_count INTEGER,
    avg_min_score REAL,
    max_score INTEGER,
    min_score INTEGER,
    eval_count INTEGER,
    a_grade_count INTEGER,
    has_a_plus INTEGER DEFAULT 0,
    career_website TEXT,
    data_completeness INTEGER DEFAULT 0
)
''')

# 2. 清理学校名称的函数
def clean_name(name):
    if pd.isna(name):
        return ''
    # 移除括号及其内容
    name = re.sub(r'[（\(\【\【].*?[）\)\】\】]', '', name)
    # 移除"民办"等标记
    name = re.sub(r'[（\(].*', '', name)
    return name.strip()

# 3. 从admission_records获取高校信息
print("[2] 提取录取数据中的高校信息...")
admission_info = pd.read_sql('''
    SELECT
        school_name,
        MAX(year) as latest_year,
        COUNT(DISTINCT major_name) as major_count,
        COUNT(*) as record_count,
        AVG(min_score) as avg_min_score,
        MAX(min_score) as max_score,
        MIN(min_score) as min_score
    FROM admission_records
    GROUP BY school_name
''', conn)
admission_info['clean_name'] = admission_info['school_name'].apply(clean_name)
print(f"    提取到 {len(admission_info)} 所高校")

# 4. 学科评估信息
print("[3] 提取学科评估信息...")
discipline_info = pd.read_sql('''
    SELECT
        school_name,
        COUNT(*) as eval_count,
        SUM(CASE WHEN rating IN ('A+', 'A', 'A-') THEN 1 ELSE 0 END) as a_grade_count,
        MAX(CASE WHEN rating = 'A+' THEN 1 ELSE 0 END) as has_a_plus
    FROM discipline_evaluations
    GROUP BY school_name
''', conn)
discipline_info['clean_name'] = discipline_info['school_name'].apply(clean_name)
print(f"    提取到 {len(discipline_info)} 所高校")

# 5. 就业网站信息
print("[4] 提取就业网站信息...")
career_info = pd.read_sql('''
    SELECT school_name, website_url
    FROM career_websites
''', conn)
career_info['clean_name'] = career_info['school_name'].apply(clean_name)
print(f"    提取到 {len(career_info)} 所高校")

# 6. 合并数据
print("[5] 合并数据...")
integrated = admission_info.copy()
integrated = integrated.merge(
    discipline_info[['clean_name', 'eval_count', 'a_grade_count', 'has_a_plus']],
    on='clean_name',
    how='left'
)
integrated = integrated.merge(
    career_info[['clean_name', 'website_url']],
    on='clean_name',
    how='left'
)

# 计算数据完整度
integrated['data_completeness'] = (
    integrated['website_url'].notna().astype(int) * 25 +
    integrated['eval_count'].notna().astype(int) * 25 +
    integrated['a_grade_count'].fillna(0).astype(int).gt(0).astype(int) * 25 +
    integrated['record_count'].notna().astype(int) * 25
)

# 7. 插入数据库
print("[6] 插入数据到数据库...")

# 先清空表
cur.execute('DELETE FROM integrated_schools')

for _, row in integrated.iterrows():
    cur.execute('''
        INSERT INTO integrated_schools (
            school_name, latest_year, major_count, record_count,
            avg_min_score, max_score, min_score,
            eval_count, a_grade_count, has_a_plus,
            career_website, data_completeness
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['school_name'],
        row['latest_year'],
        int(row['major_count']) if pd.notna(row['major_count']) else None,
        int(row['record_count']) if pd.notna(row['record_count']) else None,
        row['avg_min_score'] if pd.notna(row['avg_min_score']) else None,
        int(row['max_score']) if pd.notna(row['max_score']) else None,
        int(row['min_score']) if pd.notna(row['min_score']) else None,
        int(row['eval_count']) if pd.notna(row['eval_count']) else None,
        int(row['a_grade_count']) if pd.notna(row['a_grade_count']) else None,
        int(row['has_a_plus']) if pd.notna(row['has_a_plus']) else 0,
        row['website_url'] if pd.notna(row['website_url']) else None,
        int(row['data_completeness'])
    ))

conn.commit()

# 8. 统计
print("\n" + "=" * 60)
print("数据保存完成!")
print("=" * 60)

cur.execute('SELECT COUNT(*) FROM integrated_schools')
total = cur.fetchone()[0]
print(f"总记录数: {total}")

cur.execute('SELECT COUNT(*) FROM integrated_schools WHERE career_website IS NOT NULL')
with_career = cur.fetchone()[0]
print(f"有就业网站: {with_career} ({with_career/total*100:.1f}%)")

cur.execute('SELECT COUNT(*) FROM integrated_schools WHERE eval_count IS NOT NULL')
with_eval = cur.fetchone()[0]
print(f"有学科评估: {with_eval} ({with_eval/total*100:.1f}%)")

cur.execute('SELECT COUNT(*) FROM integrated_schools WHERE has_a_plus = 1')
with_a_plus = cur.fetchone()[0]
print(f"有A+学科: {with_a_plus}")

# 9. 创建视图方便查询
print("\n[7] 创建便捷视图...")

# 创建985/211高校视图
cur.execute('''
CREATE OR REPLACE VIEW top_schools AS
SELECT * FROM integrated_schools
WHERE data_completeness >= 75
ORDER BY data_completeness DESC, record_count DESC
''')

# 显示Top 10数据完整度最高的高校
print("\n数据完整度最高的高校 (Top 10):")
cur.execute('''
SELECT school_name, latest_year, major_count, eval_count, career_website, data_completeness
FROM integrated_schools
ORDER BY data_completeness DESC, record_count DESC
LIMIT 10
''')
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}年 | 专业{row[2]} | 学科评估{row[3]} | 就业网{'✓' if row[4] else '✗'} | 完整度{row[5]}%")

conn.close()
print("\n数据库更新完成!")
