"""
高校就业网站智能发现脚本 v2

策略：
1. 通过高校名称生成可能的域名和URL模式
2. 检测HTTP状态码来判断就业网站是否存在
3. 记录发现结果供人工确认
"""

import sqlite3
import requests
import time
import random
from datetime import datetime

db_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'

# 常见的就业网站子域名和路径模式
CAREER_PATTERNS = [
    # 子域名（最常见）
    'http://career.{domain}',
    'http://job.{domain}',
    'http://jiuye.{domain}',
    'http://zhaopin.{domain}',
    'http://yxjy.{domain}',      # 优先就业
    'http://jyxx.{domain}',      # 就业信息
    'http://jygl.{domain}',      # 就业管理
    'http://jyzx.{domain}',      # 就业中心
    'http://zjy.{domain}',       # 招生就业
    'http://zpxx.{domain}',       # 招聘信息
    'http://career2.{domain}',
    'http://job2.{domain}',
    'https://career.{domain}',
    'https://job.{domain}',
    'https://jiuye.{domain}',
    # 常见路径
    'http://{domain}/career/',
    'http://{domain}/job/',
    'http://{domain}/jiuye/',
    'http://{domain}/zhaopin/',
    'http://{domain}/Employment/',
    'http://{domain}/jy/',
]

def get_schools_to_probe():
    """获取待探测的学校列表"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 获取已有就业网站的高校
    cursor.execute("SELECT school_name FROM career_websites")
    existing = set(row[0] for row in cursor.fetchall())

    # 获取有官网的高校（如果有website字段）
    cursor.execute("SELECT name, website FROM schools WHERE website IS NOT NULL AND website != ''")
    schools_with_website = {row[0]: row[1] for row in cursor.fetchall() if row[1]}

    # 获取所有学校名称
    cursor.execute("SELECT name FROM schools WHERE name LIKE '%大学%' OR name LIKE '%学院%'")
    all_schools = [row[0] for row in cursor.fetchall()]

    conn.close()

    # 过滤并返回待探测学校
    schools_without_career = [s for s in all_schools if s not in existing]

    # 生成探测候选
    candidates = []
    for school in schools_without_career[:500]:  # 限制数量
        domain = generate_domain(school)
        if domain:
            candidates.append({
                'school': school,
                'domain': domain,
                'patterns': [p.replace('{domain}', domain) for p in CAREER_PATTERNS]
            })

    return candidates, schools_with_website

def generate_domain(school_name):
    """根据学校名称生成可能的域名"""
    # 移除常见后缀
    name = school_name
    for suffix in ['大学', '学院', '（分校区）', '（独立学院）', '有限责任公司']:
        name = name.replace(suffix, '')

    # 处理括号内容
    if '(' in name:
        name = name.split('(')[0]

    # 清理
    name = name.replace(' ', '').replace('-', '')

    # 如果名称太长或太短，尝试其他方式
    if len(name) <= 2:
        return None

    # 常见edu.cn域名
    return name.lower() + '.edu.cn'

def probe_url(url, timeout=3):
    """探测URL是否可访问"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code
    except requests.exceptions.SSLError:
        try:
            response = requests.head(url.replace('https', 'http'), timeout=timeout)
            return response.status_code
        except:
            return None
    except:
        return None

def discover():
    """执行发现流程"""
    print(f"高校就业网站发现 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    candidates, schools_with_website = get_schools_to_probe()

    print(f"待探测学校: {len(candidates)} 所")
    print(f"已有官网数据: {len(schools_with_website)} 所")

    discovered = []
    not_found = []

    for i, item in enumerate(candidates):
        school = item['school']
        domain = item['domain']
        patterns = item['patterns'][:8]  # 限制每个学校探测的pattern数

        print(f"\n[{i+1}/{len(candidates)}] 探测: {school}")

        found = False
        for url in patterns:
            status = probe_url(url)
            if status and status < 400:
                print(f"  [发现] {url} (状态:{status})")
                discovered.append({
                    'school': school,
                    'url': url,
                    'domain': domain,
                    'status': status
                })
                found = True
                break
            elif status:
                print(f"  [--] {url} (状态:{status})")
            else:
                print(f"  [x] {url}")

        if not found:
            not_found.append(school)

        # 随机延时避免被封
        time.sleep(random.uniform(0.2, 0.5))

        # 每100个输出进度
        if (i + 1) % 100 == 0:
            print(f"\n进度: {i+1}/{len(candidates)}, 发现: {len(discovered)}")

    return discovered, not_found

def save_results(discovered):
    """保存发现结果"""
    output_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\discovered_career_websites.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 高校就业网站发现结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 共发现 {len(discovered)} 个可能的就业网站\n\n")

        for item in discovered:
            f.write(f"{item['school']}|{item['url']}|{item['status']}\n")

    print(f"\n结果已保存到: {output_file}")

    # 同时输出CSV格式方便查看
    csv_file = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\discovered_career_websites.csv'
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("学校名称,就业网站URL,状态码\n")
        for item in discovered:
            f.write(f"{item['school']},{item['url']},{item['status']}\n")

    print(f"CSV已保存到: {csv_file}")

if __name__ == "__main__":
    discovered, not_found = discover()

    print("\n" + "=" * 60)
    print(f"探测完成!")
    print(f"发现: {len(discovered)} 个")
    print(f"未找到: {len(not_found)} 所")

    if discovered:
        save_results(discovered)
