"""
高校数据整合脚本 v2

整合多个数据源，建立清晰的高校信息表
"""

import sqlite3
import pandas as pd
from datetime import datetime

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'
output_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_integrated_schools.xlsx'

print(f"高校数据整合 v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

conn = sqlite3.connect(db_file)

# 1. 从schools表提取"干净"的高校数据
# 条件：名称长度适中、包含"大学"或"学院"、不包含特殊字符
print("\n[1] 提取高校基础信息...")
base_schools = pd.read_sql('''
    SELECT DISTINCT
        code as school_code,
        name as school_name,
        province,
        city,
        tier,
        CASE
            WHEN tier = '985工程' THEN '985'
            WHEN tier = '一流学科建设高校' THEN '双一流'
            WHEN is_211 = 1 THEN '211'
            ELSE '普通'
        END as level,
        school_type
    FROM schools
    WHERE name LIKE '%大学' OR name LIKE '%学院'
    AND LENGTH(name) BETWEEN 4 AND 20
    AND name NOT LIKE '%委员会%'
    AND name NOT LIKE '%办公室%'
    AND name NOT LIKE '%服务中心%'
    AND name NOT LIKE '%研究院%'
    AND name NOT LIKE '%实验室%'
    AND name NOT LIKE '%中心%'
    AND name NOT LIKE '%基地%'
    AND name NOT LIKE '%分部%'
    AND name NOT LIKE '%校区%'
    AND name NOT LIKE '%教学%'
    AND name NOT LIKE '%服务%'
    AND name NOT LIKE '%培训%'
    AND name NOT LIKE '%联络%'
    AND name NOT LIKE '%合作%'
''', conn)

print(f"   提取到 {len(base_schools)} 所高校")

# 2. 从admission_records获取高校最近录取信息
print("[2] 提取录取数据...")
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

print(f"   提取到 {len(admission_info)} 所高校的录取数据")

# 3. 学科评估信息
print("[3] 提取学科评估...")
discipline_info = pd.read_sql('''
    SELECT
        school_name,
        COUNT(*) as eval_count,
        SUM(CASE WHEN rating IN ('A+', 'A', 'A-') THEN 1 ELSE 0 END) as a_grade_count,
        MAX(CASE WHEN rating = 'A+' THEN 1 ELSE 0 END) as has_a_plus
    FROM discipline_evaluations
    GROUP BY school_name
''', conn)

print(f"   提取到 {len(discipline_info)} 所高校的学科评估")

# 4. 就业网站
print("[4] 提取就业网站...")
career_info = pd.read_sql('''
    SELECT school_name, website_url, province as career_province
    FROM career_websites
''', conn)

print(f"   提取到 {len(career_info)} 所高校的就业网站")

# 整合数据
print("\n" + "=" * 60)
print("数据整合...")

# 由于学校名称可能有差异，使用模糊匹配
# 首先创建统一的高校名称（清理括号内容）
def clean_name(name):
    if pd.isna(name):
        return ''
    import re
    # 移除括号及其内容
    name = re.sub(r'[（\(\【\【].*?[）\)\】\】]', '', name)
    # 移除"民办"等标记
    name = re.sub(r'[（\(].*', '', name)
    return name.strip()

admission_info['clean_name'] = admission_info['school_name'].apply(clean_name)
career_info['clean_name'] = career_info['school_name'].apply(clean_name)
discipline_info['clean_name'] = discipline_info['school_name'].apply(clean_name)

# 合并
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

# 统计
print("\n" + "=" * 60)
print("整合结果统计")
print("=" * 60)

total = len(integrated)
with_career = integrated['website_url'].notna().sum()
with_discipline = integrated['eval_count'].notna().sum()
with_grade_a = (integrated['a_grade_count'] > 0).sum() if 'a_grade_count' in integrated.columns else 0

print(f"高校总数: {total}")
print(f"有就业网站: {with_career} ({with_career/total*100:.1f}%)")
print(f"有学科评估: {with_discipline} ({with_discipline/total*100:.1f}%)")
print(f"有A等级学科: {with_grade_a} ({with_grade_a/total*100:.1f}%)")

# 输出到Excel
output_df = integrated[[
    'school_name', 'latest_year', 'major_count', 'record_count',
    'avg_min_score', 'max_score', 'min_score',
    'eval_count', 'a_grade_count', 'has_a_plus', 'website_url'
]].copy()

output_df.columns = [
    '学校名称', '最新年份', '专业数', '录取记录数',
    '平均最低分', '最高分', '最低分',
    '学科评估数', 'A等级数', '有A+', '就业网站'
]

output_df = output_df.sort_values('录取记录数', ascending=False)
output_df.to_excel(output_file, index=False, engine='openpyxl')

print(f"\n已保存到: {output_file}")

# 显示Top 30
print("\n" + "=" * 60)
print("数据样本 (Top 30 by 录取记录数):")
print("=" * 60)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(output_df.head(30).to_string())

conn.close()
