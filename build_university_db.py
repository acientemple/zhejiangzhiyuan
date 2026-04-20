import re
import sqlite3
import os

# 文件路径
sql_file = r"C:\Users\Lenovo\OneDrive\Info\填报志愿\data\最新全国高校数据库信息（包含2854所高校）+全国地区数据表\districts.sql"
db_file = r"C:\Users\Lenovo\OneDrive\Desktop\projects\zhejiangzhiyuan\universities.db"

# 读取SQL文件
with open(sql_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有 school INSERT 语句
pattern = r"INSERT INTO `school` VALUES \((.+?)\);"
matches = re.findall(pattern, content, re.DOTALL)

print(f"找到 {len(matches)} 条原始记录")

# 连接数据库
if os.path.exists(db_file):
    os.remove(db_file)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE universities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    province TEXT,
    city TEXT,
    district TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL
)
''')

# 从地址中移除省市区前缀
def clean_address(address, province, city, district):
    if not address:
        return address

    # 按优先级尝试移除
    # 先移除直辖市/特别行政区前缀 (如 "北京市" -> "")
    # 再移除市辖区前缀

    cleaned = address

    # 移除省级前缀
    if province and province in cleaned:
        cleaned = cleaned.replace(province, '')

    # 移除城市前缀
    if city and city in cleaned:
        cleaned = cleaned.replace(city, '')

    # 移除区级前缀
    if district and district in cleaned:
        cleaned = cleaned.replace(district, '')

    # 清理多余的"省"、"市"、"区"、"县"开头
    cleaned = re.sub(r'^省\s*', '', cleaned)
    cleaned = re.sub(r'^市\s*', '', cleaned)
    cleaned = re.sub(r'^区\s*', '', cleaned)
    cleaned = re.sub(r'^县\s*', '', cleaned)

    # 清理可能残留的括号内容（如 "(东校区)"）
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)

    # 去除多余空格和标点
    cleaned = cleaned.strip()
    cleaned = re.sub(r'^\s*[\-,:，：\s]+', '', cleaned)

    return cleaned if cleaned else address

# 解析每条记录
university_count = 0

for match in matches:
    try:
        # 手动拆分字段
        fields = []
        current = ''
        in_quotes = False
        i = 0

        while i < len(match):
            char = match[i]
            if char == "'" and (i == 0 or match[i-1] != '\\'):
                in_quotes = not in_quotes
                current += char
            elif char == ',' and not in_quotes:
                fields.append(current.strip().strip("'"))
                current = ''
            else:
                current += char
            i += 1
        if current.strip():
            fields.append(current.strip().strip("'"))

        if len(fields) >= 13:
            uid = int(fields[0]) if fields[0].isdigit() else 0
            name = fields[3]
            raw_province_id = int(fields[4]) if fields[4].isdigit() else 0
            raw_city_id = int(fields[5]) if fields[5].isdigit() else 0
            raw_district_id = int(fields[6]) if fields[6].isdigit() else 0
            address = fields[7]
            longitude = float(fields[8]) if fields[8] and fields[8].replace('.','').replace('-','').isdigit() else 0
            latitude = float(fields[9]) if fields[9] and fields[9].replace('.','').replace('-','').isdigit() else 0
            province = fields[10]
            city = fields[11]
            district = fields[12]

            # 清理地址
            clean_addr = clean_address(address, province, city, district)

            cursor.execute('''
                INSERT INTO universities (id, name, province, city, district, address, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (uid, name, province, city, district, clean_addr, latitude, longitude))
            university_count += 1

    except Exception as e:
        pass

conn.commit()

# 验证数据
cursor.execute("SELECT COUNT(*) FROM universities")
total = cursor.fetchone()[0]

cursor.execute("SELECT province, COUNT(*) FROM universities GROUP BY province ORDER BY COUNT(*) DESC")
by_province = cursor.fetchall()

print(f"\n成功导入 {university_count} 所高校")

print(f"\n各省份高校数量:")
for prov, count in by_province:
    print(f"  {prov}: {count}")

# 显示清理后的示例数据
print("\n清理后的示例数据:")
cursor.execute("SELECT name, province, city, district, address FROM universities LIMIT 5")
for row in cursor.fetchall():
    print(f'  {row[0]}')
    print(f'    省份: {row[1]}, 城市: {row[2]}, 区: {row[3]}')
    print(f'    详细地址: {row[4]}')
    print()

conn.close()
print(f"数据库已创建: {db_file}")
