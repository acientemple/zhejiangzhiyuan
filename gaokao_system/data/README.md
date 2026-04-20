# 高考志愿填报数据库系统

## 项目概述

本项目整合了多个数据源，构建了一个全面的高考志愿填报辅助决策数据库，涵盖全国高校信息、录取数据、学科评估、选考科目要求等核心数据，并为未来扩展就业率、满意度等指标预留了接口。

## 数据库文件

**路径：** `D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db`

**类型：** SQLite 数据库

## 数据库结构

### 1. schools（高校信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| code | VARCHAR(20) | 学校代码 |
| name | TEXT | 学校名称（唯一） |
| province | TEXT | 所在省份 |
| city | TEXT | 所在城市 |
| district | TEXT | 所在区县 |
| address | TEXT | 详细地址 |
| latitude | REAL | 纬度 |
| longitude | REAL | 经度 |
| is_985 | BOOLEAN | 是否985工程 |
| is_211 | BOOLEAN | 是否211工程 |
| is_double_first_class | BOOLEAN | 是否双一流 |
| school_type | VARCHAR(50) | 学校类型（综合/理工/师范等） |
| tier | VARCHAR(50) | 层次（985工程/一流学科建设高校/普通高校） |
| tier_rank | INTEGER | 在该层次的排名 |
| score | REAL | 办学水平评分 |
| website | VARCHAR(200) | 学校官网 |
| source | VARCHAR(20) | 数据来源 |

**记录数：** 12,499 所

### 2. majors（专业信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| school_id | INTEGER | 所属学校ID |
| code | VARCHAR(20) | 专业代码 |
| name | TEXT | 专业名称 |
| category | TEXT | 学科门类（工学/理学/文学等） |
| first_level | TEXT | 一级学科 |
| second_level | TEXT | 二级学科 |
| study_years | INTEGER | 学制（年） |
| degree_type | VARCHAR(20) | 学位类型 |
| discipline_eval | VARCHAR(10) | 学科评估等级 |
| level | VARCHAR(20) | 层次（本科/专科） |
| source | VARCHAR(20) | 数据来源 |

**记录数：** 39,012

### 3. admission_records（录取记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| year | INTEGER | 录取年份 |
| batch | TEXT | 录取批次（一段/二段） |
| school_id | INTEGER | 学校ID |
| school_name | TEXT | 学校名称 |
| major_id | INTEGER | 专业ID |
| major_name | TEXT | 专业名称 |
| enrollment_plan | INTEGER | 招生计划数 |
| actual_count | INTEGER | 实际录取数 |
| min_score | INTEGER | 最低录取分数 |
| min_rank | INTEGER | 最低录取位次 |
| avg_score | REAL | 平均分 |
| score_line | INTEGER | 分数线 |
| rank_position | REAL | 位次 |
| source | VARCHAR(20) | 数据来源 |

**记录数：** 163,148

### 4. disciplines（学科分类表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| category | TEXT | 学科门类 |
| first_level_code | TEXT | 一级学科代码 |
| first_level | TEXT | 一级学科名称 |
| second_level_code | TEXT | 二级学科代码 |
| second_level | TEXT | 二级学科名称 |

**学科门类（13个）：**
- 哲学、经济学、法学、教育学、文学、历史学
- 理学、工学、农学、医学、军事学、管理学、艺术学

**记录数：** 253

### 5. discipline_evaluations（学科评估表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| discipline_code | TEXT | 学科代码 |
| discipline_name | TEXT | 学科名称 |
| rating | TEXT | 评估等级（A+/A/A-/B+等） |
| school_code | TEXT | 学校代码 |
| school_name | TEXT | 学校名称 |

**数据来源：** 第四轮学科评估结果

**记录数：** 5,160

### 6. subject_requirements（选考科目要求表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| year_type | VARCHAR(20) | 年份类型（2026/2027） |
| province | TEXT | 省份 |
| school_id | INTEGER | 学校ID |
| school | TEXT | 学校名称 |
| level | TEXT | 层次（本科/专科） |
| major_class | TEXT | 专业类 |
| major | TEXT | 具体专业 |
| requirement | TEXT | 选考科目要求 |
| source | VARCHAR(20) | 数据来源 |

**记录数：** 146,445（2026年 + 2027年）

### 7. professional_evaluations（专业评价表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| major_name | TEXT | 专业名称 |
| category | TEXT | 学科门类 |
| tier | VARCHAR(20) | 专业层次 |
| employment_rate | REAL | 就业率 |
| avg_salary | REAL | 平均薪资 |
| is_pitfall | BOOLEAN | 是否"坑"专业 |
| need_postgraduate | BOOLEAN | 是否需要考研 |
| study_years | INTEGER | 学制 |
| description | TEXT | 专业描述 |
| best_schools | TEXT | 推荐院校 |
| suitable_crowd | TEXT | 适合人群 |
| warning | TEXT | 注意事项 |

**记录数：** 36

### 8. school_indicators（学校指标表）

预留扩展字段，用于存储未来丰富的就业和满意度数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| school_id | INTEGER | 学校ID |
| year | INTEGER | 数据年份 |

**就业相关指标：**
- employment_rate - 就业率
- average_salary - 平均薪资
- employment_location_rate - 本地就业率

**满意度指标：**
- graduate_satisfaction - 毕业生满意度
- employer_satisfaction - 用人单位满意度

**社会影响力指标：**
- social_influence_score - 社会影响力评分
- popular_score - 口碑评分

**其他指标：**
- research_funding - 科研经费
- employment_quality_score - 就业质量评分
- description - 说明
- data_source - 数据来源

### 9. career_websites（高校就业网站表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| province | TEXT | 省份 |
| school_name | TEXT | 学校名称 |
| website_url | TEXT | 就业网站链接 |
| source | TEXT | 数据来源 |

**记录数：** 286 所（31个省级行政区）

**数据来源：** GitHub - PotoYang/UniversityCareerWebPage

### 10. integrated_schools（整合高校信息表）

整合多个数据源（录取数据、学科评估、就业网站）的高校综合信息表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| school_name | TEXT | 学校名称 |
| latest_year | INTEGER | 最新录取年份 |
| major_count | INTEGER | 专业数量 |
| record_count | INTEGER | 录取记录数 |
| avg_min_score | REAL | 平均最低录取分 |
| max_score | INTEGER | 最高录取分 |
| min_score | INTEGER | 最低录取分 |
| eval_count | INTEGER | 学科评估数量 |
| a_grade_count | INTEGER | A等级学科数 |
| has_a_plus | INTEGER | 是否有A+学科 |
| career_website | TEXT | 就业网站链接 |
| data_completeness | INTEGER | 数据完整度(0-100) |

**记录数：** 2,290 所

**视图：** `top_schools` - 数据完整度>=75的高质量高校视图

## 数据来源

| 数据项 | 来源文件 |
|--------|----------|
| 高校基本信息 | districts.sql（12,200所） |
| 浙江高考录取数据 | 历年录取信息/*.xls（2021-2025） |
| 学科评估 | 第四轮学科评估结果.pdf |
| 学科分类 | 学科分类.doc |
| 选考科目要求 | 2024/2027年普通高校招生专业选考科目要求.pdf |
| 高校层次 | 办学层次.xlsx |

## 使用示例

### Python 连接数据库

```python
import sqlite3

db_path = r'D:\work\OneDrive\Desktop\projects\zhejiangzhiyuan\gaokao_system\data\gaokao_integrated.db'
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
-- 查询所有985工程高校
SELECT name, province, score FROM schools WHERE tier = '985工程' ORDER BY tier_rank;

-- 查询某学校的学科评估
SELECT discipline_name, rating FROM discipline_evaluations WHERE school_name LIKE '%浙江大学%';

-- 查询某专业的选考要求
SELECT school, major_class, requirement FROM subject_requirements WHERE major LIKE '%计算机%';

-- 查询数据最完整的高校（整合视图）
SELECT * FROM top_schools LIMIT 20;

-- 查询某高校的综合信息
SELECT * FROM integrated_schools WHERE school_name = '浙江大学';

-- 查询有A+学科的高校
SELECT school_name, eval_count, a_grade_count FROM integrated_schools WHERE has_a_plus = 1;
```

## 未来扩展

1. **就业数据扩展**
   - 添加各高校就业率
   - 添加平均薪资数据
   - 添加就业地域分布

2. **满意度调查**
   - 毕业生满意度
   - 用人单位满意度
   - 校友评价

3. **社会影响力**
   - 大学排名
   - 口碑评分
   - 科研影响力

## 版本历史

- **v1.1** (2026-04-19): 新增高校就业网站表career_websites，共286条记录
- **v1.0** (2026-04-19): 初始版本，整合8个数据表，共366,553条记录
