import fitz
import re
import sqlite3
import os

# 文件路径
pdf_file = r"C:\Users\Lenovo\OneDrive\Info\填报志愿\data\2024年普通高校招生专业选考科目要求.pdf"
db_file = r"C:\Users\Lenovo\OneDrive\Desktop\projects\zhejiangzhiyuan\universities.db"

# 打开PDF
doc = fitz.open(pdf_file)
print(f"PDF总页数: {len(doc)}")

# 存储数据
subject_requirements = []

# 合并跨行的类中所含专业
def merge_multiline_text(lines, start_idx, end_markers):
    """合并跨行的文本，直到遇到结束标记"""
    result = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        # 检查是否是结束标记行
        if any(marker in line for marker in end_markers):
            break
        result.append(line)
        i += 1
    return ''.join(result), i  # 返回合并后的文本和处理的行数

# 解析每一页
def parse_page(text):
    """解析单个页面的文本"""
    results = []
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行、标题、页脚
        if not line or '浙江省教育考试院' in line or '第' in line and '页' in line:
            i += 1
            continue

        # 跳过表头
        if line in ['省份', '院校名称', '专业（类）名称', '类中所含专业', '层次', '选考科目要求']:
            i += 1
            continue

        # 省份识别（简短地名，通常2-4个汉字）
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

                # 下一个非空行是专业（类）名称
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                major_class = lines[i].strip()
                i += 1

                # 检查是否有类中所含专业（下一行不是"本科"或"专科"）
                majors_in_class = ''
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    # 如果是层次标记，说明没有类中所含专业
                    if '本科' in next_line or '专科' in next_line:
                        level = '本科' if '本科' in next_line else '专科'
                        i += 1
                        # 下一行是选考科目要求
                        if i < len(lines):
                            requirement = lines[i].strip()
                            i += 1
                        else:
                            requirement = ''
                        break
                    # 否则这行是类中所含专业（可能跨多行）
                    else:
                        majors_in_class += next_line
                        i += 1
                        # 继续读取直到遇到"本科"或"专科"
                        while i < len(lines):
                            check_line = lines[i].strip()
                            if not check_line:
                                i += 1
                                continue
                            if '本科' in check_line or '专科' in check_line:
                                level = '本科' if '本科' in check_line else '专科'
                                i += 1
                                if i < len(lines):
                                    requirement = lines[i].strip()
                                    i += 1
                                else:
                                    requirement = ''
                                break
                            else:
                                majors_in_class += check_line
                                i += 1
                        break

                # 如果有类中所含专业，拆分并创建多条记录
                if majors_in_class:
                    # 清理专业列表字符串
                    majors_in_class = majors_in_class.replace('\n', '').replace(' ', '')
                    # 按"、"拆分
                    majors = re.split(r'[、，,]', majors_in_class)
                    for major in majors:
                        major = major.strip()
                        if major:
                            results.append({
                                'province': province,
                                'school': school,
                                'major_class': major_class,
                                'major': major,
                                'level': level,
                                'requirement': requirement
                            })
                else:
                    # 没有类中所含专业，只有专业（类）名称本身
                    results.append({
                        'province': province,
                        'school': school,
                        'major_class': major_class,
                        'major': '',
                        'level': level,
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
    subject_requirements.extend(results)

    if (page_num + 1) % 200 == 0:
        print(f"已处理页面 {page_num + 1}/{len(doc)}")

print(f"\n提取到 {len(subject_requirements)} 条原始记录")

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建选考科目要求表
cursor.execute('''
CREATE TABLE IF NOT EXISTS subject_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    province TEXT NOT NULL,
    school TEXT NOT NULL,
    major_class TEXT,
    major TEXT,
    level TEXT NOT NULL,
    requirement TEXT NOT NULL
)
''')

# 插入数据
for record in subject_requirements:
    cursor.execute('''
        INSERT INTO subject_requirements (province, school, major_class, major, level, requirement)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (record['province'], record['school'], record['major_class'], record['major'],
          record['level'], record['requirement']))

conn.commit()

# 统计
cursor.execute("SELECT COUNT(*) FROM subject_requirements")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT school) FROM subject_requirements")
school_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT province) FROM subject_requirements")
province_count = cursor.fetchone()[0]

# 按选考要求统计
cursor.execute("SELECT requirement, COUNT(*) FROM subject_requirements GROUP BY requirement ORDER BY COUNT(*) DESC")
req_dist = cursor.fetchall()

print(f"\n数据库更新完成!")
print(f"总记录数: {total}")
print(f"涉及高校: {school_count}")
print(f"涉及省份: {province_count}")

print("\n选考要求分布 (TOP 10):")
for req, cnt in req_dist[:10]:
    print(f"  {req}: {cnt}")

# 示例数据 - 北京大学文科试验班类
print("\n示例数据 (北京大学 文科试验班类):")
cursor.execute('''
    SELECT province, school, major_class, major, level, requirement
    FROM subject_requirements
    WHERE school LIKE '%北京大学%' AND major_class LIKE '%文科试验班%'
    ORDER BY major
    LIMIT 15
''')
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")

# 北京大学城乡规划
print("\n示例数据 (北京大学 城乡规划):")
cursor.execute('''
    SELECT province, school, major_class, major, level, requirement
    FROM subject_requirements
    WHERE school LIKE '%北京大学%' AND major = '城乡规划'
''')
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")

conn.close()
doc.close()

print(f"\n数据库已更新: {db_file}")
