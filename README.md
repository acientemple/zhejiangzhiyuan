# 高考志愿填报数据库系统

## 项目概述

本项目整合了多个数据源，构建了一个全面的高考志愿填报辅助决策数据库，涵盖全国高校信息、录取数据、学科评估、选考科目要求、就业网站等核心数据。

## 项目结构

```
zhejiangzhiyuan/
├── gaokao_system/
│   ├── data/
│   │   ├── gaokao_integrated.db    # 主数据库（SQLite）
│   │   ├── 中国高校名单.xlsx        # 高校名单导出
│   │   └── README.md               # 数据库说明
│   └── ...
├── build_*.py                      # 数据构建脚本
├── update_*.py                      # 数据更新脚本
├── integrate_*.py                  # 数据整合脚本
└── README.md
```

## 数据库

**路径：** `gaokao_system/data/gaokao_integrated.db`

### 数据表

| 表名 | 说明 | 记录数 |
|------|------|--------|
| schools | 高校信息 | 12,499 |
| majors | 专业信息 | 39,012 |
| admission_records | 录取记录 | 163,148 |
| disciplines | 学科分类 | 253 |
| discipline_evaluations | 学科评估 | 5,160 |
| subject_requirements | 选考科目要求 | 146,445 |
| professional_evaluations | 专业评价 | 36 |
| school_indicators | 学校指标(预留) | 0 |
| career_websites | 就业网站 | 286 |
| integrated_schools | 整合高校信息 | 2,290 |
| zhejiang_recruiting_schools | 在浙招生高校 | 1,717 |

## 快速开始

### Python 连接数据库

```python
import sqlite3

db_path = 'gaokao_system/data/gaokao_integrated.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询示例：浙江大学在浙江的录取数据
cursor.execute('''
    SELECT year, batch, major_name, min_score, min_rank
    FROM admission_records
    WHERE school_name = '浙江大学' AND year = 2024
    ORDER BY batch, min_score DESC
''')
for row in cursor.fetchall():
    print(row)

conn.close()
```

### 查询示例

```sql
-- 查询数据最完整的高校
SELECT * FROM top_schools LIMIT 20;

-- 查询某学校的学科评估
SELECT discipline_name, rating FROM discipline_evaluations
WHERE school_name LIKE '%浙江大学%';

-- 查询某专业的选考要求
SELECT school, major_class, requirement FROM subject_requirements
WHERE major LIKE '%计算机%';

-- 查询有A+学科的高校
SELECT school_name, eval_count FROM integrated_schools
WHERE has_a_plus = 1;

-- 查询在浙招生高校（在浙招生高校表）
SELECT * FROM zhejiang_top_schools LIMIT 20;

-- 查询某高校在浙招生年份
SELECT school_name, first_year, latest_year FROM zhejiang_recruiting_schools
WHERE school_name LIKE '%浙江大学%';
```

## 数据来源

| 数据项 | 来源 |
|--------|------|
| 高校基本信息 | districts.sql |
| 浙江高考录取数据 | 历年录取信息/*.xls（2021-2025） |
| 学科评估 | 第四轮学科评估结果.pdf |
| 选考科目要求 | 2024/2027年普通高校招生专业选考科目要求.pdf |
| 就业网站 | GitHub - PotoYang/UniversityCareerWebPage |

## 构建脚本

| 脚本 | 说明 |
|------|------|
| build_admission_records_db.py | 构建录取记录数据库 |
| build_discipline_evaluation_db.py | 构建学科评估数据库 |
| build_subject_requirements_db.py | 构建选考科目要求数据库 |
| build_career_websites_db.py | 构建就业网站数据库 |
| build_2027_subject_requirements_db.py | 构建2027年选考科目要求 |
| integrate_school_data.py | 整合高校数据 |
| save_integrated_data.py | 保存整合数据到数据库 |
| update_career_websites.py | 更新就业网站数据 |
| discover_career_websites.py | 发现新的就业网站 |
| build_zhejiang_schools.py | 构建在浙招生高校名单 |

## 未来扩展

1. **就业数据扩展** - 添加就业率、平均薪资、就业地域分布
2. **满意度调查** - 毕业生满意度、用人单位满意度
3. **社会影响力** - 大学排名、口碑评分、科研影响力

## 版本历史

- **v1.2** (2026-04-20): 新增integrated_schools表，整合录取、学科评估、就业网站数据
- **v1.1** (2026-04-19): 新增career_websites表，共286条就业网站记录
- **v1.0** (2026-04-19): 初始版本，8个数据表，共366,553条记录

## License

MIT
