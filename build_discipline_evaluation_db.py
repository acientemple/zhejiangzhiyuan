import fitz
import re
import sqlite3
import os

# 文件路径
pdf_file = r"D:\BaiduYunDownload\全国第四轮学科评估结果(知乎鹿十七).pdf"
db_file = r"C:\Users\Lenovo\OneDrive\Desktop\projects\zhejiangzhiyuan\universities.db"

# 打开PDF
doc = fitz.open(pdf_file)
print(f"PDF总页数: {len(doc)}")

# 存储数据
discipline_evaluations = []

# 正则表达式匹配学科代码名称和学校代码名称
# 例如: "0101 哲学" -> 学科代码 0101, 学科名称 哲学
# "10001 北京大学" -> 学校代码 10001, 学校名称 北京大学
discipline_pattern = re.compile(r'^(\d{4})\s+(.+)$')
school_pattern = re.compile(r'^(\d{5})\s+(.+)$')
rating_pattern = re.compile(r'^(A\+|A|A-|B\+|B|B-|C\+|C|C-)$')

# 当前状态
current_discipline_code = None
current_discipline_name = None
current_rating = None

def parse_page(page_text):
    """解析单个页面的文本"""
    results = []
    lines = page_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行和页脚
        if not line or '知乎' in line or '/' in line or '一、' in line or '二、' in line:
            i += 1
            continue

        # 匹配学科代码和名称 (4位数字开头)
        disc_match = discipline_pattern.match(line)
        if disc_match:
            current_discipline_code = disc_match.group(1)
            current_discipline_name = disc_match.group(2)
            i += 1
            continue

        # 匹配评估结果 (A+, A, A-, B+, B, B-, C+, C, C-)
        rating_match = rating_pattern.match(line)
        if rating_match and current_discipline_code:
            current_rating = rating_match.group(1)
            i += 1
            # 下一行应该是学校代码和名称
            if i < len(lines):
                school_line = lines[i].strip()
                school_match = school_pattern.match(school_line)
                if school_match:
                    school_code = school_match.group(1)
                    school_name = school_match.group(2)
                    results.append({
                        'discipline_code': current_discipline_code,
                        'discipline_name': current_discipline_name,
                        'rating': current_rating,
                        'school_code': school_code,
                        'school_name': school_name
                    })
            i += 1
            continue

        i += 1

    return results

# 提取所有数据 (页面17-143是按学科分类，144+是按学校分类)
print("开始提取数据...")

for page_num in range(16, min(144, len(doc))):  # 页面17-144 (索引16-143)
    page = doc[page_num]
    text = page.get_text()

    # 解析页面
    results = parse_page(text)
    discipline_evaluations.extend(results)

    if (page_num - 16 + 1) % 20 == 0:
        print(f"已处理页面 {page_num - 16 + 1}/128")

print(f"\n提取到 {len(discipline_evaluations)} 条评估记录")

# 连接到数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建学科评估表
cursor.execute('''
CREATE TABLE IF NOT EXISTS discipline_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discipline_code TEXT NOT NULL,
    discipline_name TEXT NOT NULL,
    rating TEXT NOT NULL,
    school_code TEXT,
    school_name TEXT
)
''')

# 创建学科表
cursor.execute('''
CREATE TABLE IF NOT EXISTS disciplines (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

# 插入数据
for record in discipline_evaluations:
    cursor.execute('''
        INSERT INTO discipline_evaluations (discipline_code, discipline_name, rating, school_code, school_name)
        VALUES (?, ?, ?, ?, ?)
    ''', (record['discipline_code'], record['discipline_name'], record['rating'],
          record['school_code'], record['school_name']))

# 更新学科表
cursor.execute('''
    INSERT OR IGNORE INTO disciplines (code, name)
    SELECT DISTINCT discipline_code, discipline_name FROM discipline_evaluations
''')

conn.commit()

# 统计
cursor.execute("SELECT COUNT(*) FROM discipline_evaluations")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT discipline_code) FROM discipline_evaluations")
discipline_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT school_code) FROM discipline_evaluations")
school_count = cursor.fetchone()[0]

cursor.execute("SELECT rating, COUNT(*) FROM discipline_evaluations GROUP BY rating ORDER BY rating")
rating_dist = cursor.fetchall()

print(f"\n数据库更新完成!")
print(f"总评估记录: {total}")
print(f"涉及学科数: {discipline_count}")
print(f"涉及高校数: {school_count}")

print("\n评估等级分布:")
for rating, count in rating_dist:
    print(f"  {rating}: {count}")

# 显示示例数据
print("\n示例数据 (北京大学 哲学):")
cursor.execute('''
    SELECT discipline_name, rating, school_name
    FROM discipline_evaluations
    WHERE school_name LIKE '%北京大学%' AND discipline_name = '哲学'
''')
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]} - {row[2]}")

conn.close()
doc.close()

print(f"\n数据库已更新: {db_file}")
