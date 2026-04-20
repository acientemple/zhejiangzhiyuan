"""
高校就业网站更新脚本
使用方法: python update_career_websites.py

此脚本尝试通过多种途径更新高校就业网站数据:
1. 从已收录的数据中验证链接有效性
2. 通过搜索引擎查找新的高校就业网站
3. 手动添加新发现的数据
"""

import sqlite3
import time
import requests
from datetime import datetime

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'

def check_url_validity(url, timeout=5):
    """检查URL是否有效"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

def add_new_career_websites():
    """添加新发现的高校就业网站"""
    # 这里可以手动添加新发现的数据
    new_websites = [
        # 格式: (省份, 学校名称, 就业网站URL)
        # 可以在此手动添加新发现的数据
    ]

    if not new_websites:
        print("暂无新的就业网站数据需要添加")
        return 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    added = 0
    for province, school_name, website_url in new_websites:
        cursor.execute('''
            INSERT OR IGNORE INTO career_websites (province, school_name, website_url)
            VALUES (?, ?, ?)
        ''', (province, school_name, website_url))
        if cursor.rowcount > 0:
            added += 1

    conn.commit()
    conn.close()
    return added

def validate_existing_websites():
    """验证现有就业网站链接有效性"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('SELECT id, school_name, website_url FROM career_websites')
    websites = cursor.fetchall()

    print(f"开始验证 {len(websites)} 个就业网站链接...")

    invalid_count = 0
    for id, school_name, url in websites:
        if not check_url_validity(url):
            print(f"  [!] 无效链接: {school_name} - {url}")
            invalid_count += 1
        else:
            print(f"  [✓] 有效: {school_name}")

    conn.close()
    return invalid_count

def show_statistics():
    """显示当前统计"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM career_websites")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT province) FROM career_websites")
    provinces = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT school_name) FROM career_websites")
    schools = cursor.fetchone()[0]

    print(f"\n当前就业网站统计:")
    print(f"  总记录数: {total}")
    print(f"  省份数: {provinces}")
    print(f"  高校数: {schools}")

    print(f"\n各省份分布:")
    cursor.execute("SELECT province, COUNT(*) FROM career_websites GROUP BY province ORDER BY COUNT(*) DESC")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}所")

    conn.close()

if __name__ == "__main__":
    print(f"高校就业网站更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 显示当前统计
    show_statistics()

    print("\n" + "=" * 50)
    print("开始更新...")

    # 添加新数据
    added = add_new_career_websites()
    if added > 0:
        print(f"新增 {added} 条记录")

    # 验证现有数据
    invalid = validate_existing_websites()
    if invalid > 0:
        print(f"发现 {invalid} 个无效链接")

    print("\n更新完成!")
