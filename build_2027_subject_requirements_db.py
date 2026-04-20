import fitz
import re
import sqlite3
import os

# 文件路径
pdf_file = r"C:\Users\Lenovo\OneDrive\Info\填报志愿\data\2027年及以后普通高校招生专业选考科目要求.pdf"
db_file = r"C:\Users\Lenovo\OneDrive\Desktop\projects\zhejiangzhiyuan\universities.db"

# 打开PDF
doc = fitz.open(pdf_file)
print(f"PDF总页数: {len(doc)}")

# 存储数据
subject_requirements_2027 = []

# 解析每一页
def parse_page(text):
    """解析单个页面的文本"""
    results = []
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行、页脚、标题
        if not line or '浙江省教育考试院' in line or '第' in line and '页' in line:
            i += 1
            continue

        # 跳过表头
        if line in ['地区', '院校名称', '层次', '专业（类）名称', '选考科目要求']:
            i += 1
            continue

        # 地区识别（简短地名）
        if len(line) <= 5 and not any(x in line for x in ['大学', '学院', '学校', '本科', '专科']):
            province = line
            i += 1

            # 下一个非空行应该是院校名称
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break
            school_line = lines[i].strip()

            # 院校名称包含"大学"或"学院"
            if '大学' in school_line or '学院' in school_line:
                school = school_line
                i += 1

                # 下一个非空行是层次
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                level = lines[i].strip()
                i += 1

                # 下一个非空行是专业（类）名称
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                major_class = lines[i].strip()
                i += 1

                # 下一个非空行是选考科目要求
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                requirement = lines[i].strip()
                i += 1

                results.append({
                    'province': province,
                    'school': school,
                    'level': level,
                    'major_class': major_class,
                    'requirement': requirement
                })
            else:
                i += 1
        else:
            i += 1

    return results

# 提取所有数据
print("开始提取数据...")

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()

    results = parse_page(text)
    subject_requirements_2027.extend(results)

    if (page_num + 1) % 500 == 0:
        print(f"已处理页面 {page_num + 1}/{len(doc)}")

print(f"\n提取到 {len(subject_requirements_2027)} 条原始记录")

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建2027年选考科目要求表
cursor.execute('''
CREATE TABLE IF NOT EXISTS subject_requirements_2027 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,
    school TEXT NOT NULL,
    level TEXT NOT NULL,
    major_class TEXT NOT NULL,
    requirement TEXT NOT NULL
)
''')

# 插入数据
for record in subject_requirements_2027:
    cursor.execute('''
        INSERT INTO subject_requirements_2027 (province, school, level, major_class, requirement)
        VALUES (?, ?, ?, ?, ?)
    ''', (record['province'], record['school'], record['level'], record['major_class'], record['requirement']))

conn.commit()

# 统计
cursor.execute("SELECT COUNT(*) FROM subject_requirements_2027")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT school) FROM subject_requirements_2027")
school_count = cursor.fetchone()[0]

# 按选考要求统计
cursor.execute("SELECT requirement, COUNT(*) FROM subject_requirements_2027 GROUP BY requirement ORDER BY COUNT(*) DESC")
req_dist = cursor.fetchall()

print(f"\n数据库更新完成!")
print(f"总记录数: {total}")
print(f"涉及高校: {school_count}")

print("\n选考要求分布 (TOP 10):")
for req, cnt in req_dist[:10]:
    print(f"  {req}: {cnt}")

# 示例数据
print("\n示例数据 (北京大学):")
cursor.execute('''
    SELECT province, school, level, major_class, requirement
    FROM subject_requirements_2027
    WHERE school LIKE '%北京大学%'
    ORDER BY major_class
    LIMIT 10
''')
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]}")

conn.close()
doc.close()

print(f"\n数据库已更新: {db_file}")
print("新增表: subject_requirements_2027")
