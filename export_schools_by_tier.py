"""
根据办学层次导出高校名单到Excel
"""

import sqlite3
import pandas as pd
from datetime import datetime

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'
output_dir = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan'

print(f"按办学层次导出高校名单 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# 获取schools表的层次信息
cur.execute('SELECT name, tier, school_type FROM schools WHERE tier IS NOT NULL AND tier != ""')
tier_data = {row[0]: row[1] for row in cur.fetchall()}
type_data = {row[0]: row[2] for row in cur.fetchall()}

# 获取在浙招生高校
cur.execute('''
    SELECT school_name, original_name, latest_year, total_records, batches
    FROM zhejiang_recruiting_schools
''')
schools = []
for row in cur.fetchall():
    schools.append({
        '学校名称': row[0],
        '原始名称': row[1],
        '最新招生年份': row[2],
        '录取记录数': row[3],
        '招生批次': row[4]
    })

# 匹配层次
def get_tier(name):
    for school_name, tier in tier_data.items():
        if school_name in name or name in school_name:
            # 排除独立学院
            if '学院' in name and ('独立' in name or '分院' in name or '校区' in name):
                continue
            return tier
    return '普通'

def get_school_type(name):
    for school_name, stype in type_data.items():
        if school_name in name or name in school_name:
            return stype if stype else ''
    return ''

# 分类
schools_985 = []
schools_double = []
schools_normal = []

for school in schools:
    name = school['学校名称']
    tier = get_tier(name)

    # 排除独立学院
    if '学院' in name and ('独立' in school['原始名称'] or '分院' in school['原始名称']):
        schools_normal.append(school)
        continue

    school['学校类型'] = get_school_type(name)

    if tier == '985工程':
        schools_985.append(school)
    elif tier == '一流学科建设高校':
        schools_double.append(school)
    else:
        schools_normal.append(school)

# 导出到Excel
with pd.ExcelWriter(f'{output_dir}/在浙招生高校名单_按层次分类.xlsx', engine='openpyxl') as writer:
    # 985高校
    if schools_985:
        df_985 = pd.DataFrame(schools_985)
        df_985 = df_985.sort_values('录取记录数', ascending=False)
        df_985.to_excel(writer, sheet_name='985工程', index=False)

    # 一流学科建设高校
    if schools_double:
        df_double = pd.DataFrame(schools_double)
        df_double = df_double.sort_values('录取记录数', ascending=False)
        df_double.to_excel(writer, sheet_name='一流学科建设高校', index=False)

    # 普通高校
    if schools_normal:
        df_normal = pd.DataFrame(schools_normal)
        df_normal = df_normal.sort_values('录取记录数', ascending=False)
        df_normal.to_excel(writer, sheet_name='普通高校', index=False)

# 统计
print("\n导出统计:")
print(f"  985工程: {len(schools_985)}所")
print(f"  一流学科建设高校: {len(schools_double)}所")
print(f"  普通高校: {len(schools_normal)}所")
print(f"  合计: {len(schools)}所")

print(f"\n已保存到: {output_dir}/在浙招生高校名单_按层次分类.xlsx")

conn.close()
