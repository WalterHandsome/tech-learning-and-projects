# Pandas应用

## 1. Pandas概述

Pandas 是 Wes McKinney 在2008年开发的一个强大的**分析结构化数据**的工具集。Pandas 以 NumPy 为基础（实现数据存储和运算），提供了专门用于数据分析的类型、方法和函数，对数据分析和数据挖掘提供了很好的支持。

### 1.1 Pandas的核心数据结构

- **Series**：一维数据结构，类似于带标签的数组
- **DataFrame**：二维数据结构，类似于 Excel 表格或 SQL 表
- **Index**：索引对象，为 Series 和 DataFrame 提供索引服务

### 1.2 Pandas的特点

- **处理异质数据**：DataFrame 中每个列的数据类型可以不同
- **强大的数据操作**：筛选、合并、拼接、清洗、预处理、聚合、透视等
- **与NumPy和Matplotlib集成**：可以无缝配合使用

## 2. 准备工作

### 2.1 安装Pandas

```bash
pip install pandas
```

### 2.2 导入Pandas

```python
import pandas as pd
import numpy as np
```

## 3. Series对象

### 3.1 创建Series对象

```python
# 通过列表创建
ser1 = pd.Series(data=[120, 380, 250, 360], 
                 index=['一季度', '二季度', '三季度', '四季度'])

# 通过字典创建
ser2 = pd.Series({'一季度': 320, '二季度': 180, 
                  '三季度': 300, '四季度': 405})
```

### 3.2 Series的索引

```python
# 整数索引
print(ser1[2])  # 250

# 标签索引
print(ser1['三季度'])  # 250

# 切片索引
print(ser1[1:3])  # 二季度到三季度

# 花式索引
print(ser1[['一季度', '四季度']])

# 布尔索引
print(ser1[ser1 > 300])
```

### 3.3 Series的运算

```python
# 标量运算
ser1 += 10

# 矢量运算
ser3 = ser1 + ser2

# 统计运算
print(ser1.sum())   # 总和
print(ser1.mean())  # 均值
print(ser1.max())   # 最大值
```

## 4. DataFrame对象

### 4.1 创建DataFrame对象

#### 通过二维数组创建

```python
scores = np.random.randint(60, 101, (5, 3))
courses = ['语文', '数学', '英语']
stu_ids = np.arange(1001, 1006)
df = pd.DataFrame(data=scores, columns=courses, index=stu_ids)
```

#### 通过字典创建

```python
df = pd.DataFrame({
    '语文': [62, 72, 93, 88, 93],
    '数学': [95, 65, 86, 66, 87],
    '英语': [66, 75, 82, 69, 82]
}, index=range(1001, 1006))
```

### 4.2 读取数据创建DataFrame

#### 读取CSV文件

```python
df = pd.read_csv('data.csv', index_col='id')
```

#### 读取Excel文件

```python
df = pd.read_excel('data.xlsx', sheet_name='Sheet1', index_col='Date')
```

#### 读取数据库

```python
import pymysql

conn = pymysql.connect(
    host='localhost', port=3306,
    user='root', password='password',
    database='mydb', charset='utf8mb4'
)

df = pd.read_sql('SELECT * FROM employees', conn)
conn.close()
```

### 4.3 DataFrame的属性和方法

```python
df.shape      # 形状
df.size       # 元素总数
df.index      # 行索引
df.columns    # 列索引
df.dtypes     # 数据类型
df.info()     # 数据信息
df.head()     # 前5行
df.tail()     # 后5行
df.describe() # 描述性统计
```

## 5. DataFrame的数据访问

### 5.1 列访问

```python
# 访问单列
df['语文']

# 访问多列
df[['语文', '数学']]

# 添加新列
df['总分'] = df['语文'] + df['数学'] + df['英语']
```

### 5.2 行访问

```python
# 使用loc（标签索引）
df.loc[1001]
df.loc[1001:1003]
df.loc[1001, '语文']

# 使用iloc（位置索引）
df.iloc[0]
df.iloc[0:3]
df.iloc[0, 0]

# 使用at和iat（快速访问单个值）
df.at[1001, '语文']
df.iat[0, 0]
```

### 5.3 条件筛选

```python
# 单条件筛选
df[df['语文'] > 80]

# 多条件筛选
df[(df['语文'] > 80) & (df['数学'] > 80)]

# 使用query方法
df.query('语文 > 80 and 数学 > 80')
```

## 6. 数据重塑

### 6.1 数据拼接

```python
# 垂直拼接
df_all = pd.concat([df1, df2])

# 水平拼接
df_all = pd.concat([df1, df2], axis=1)

# 忽略索引
df_all = pd.concat([df1, df2], ignore_index=True)
```

### 6.2 数据合并

```python
# 内连接
df_merged = pd.merge(df1, df2, how='inner', on='key')

# 左连接
df_merged = pd.merge(df1, df2, how='left', on='key')

# 右连接
df_merged = pd.merge(df1, df2, how='right', on='key')

# 外连接
df_merged = pd.merge(df1, df2, how='outer', on='key')

# 不同列名
df_merged = pd.merge(df1, df2, left_on='key1', right_on='key2')
```

### 6.3 数据透视

```python
# 透视表
df_pivot = pd.pivot_table(df, values='score', 
                          index='name', columns='subject')

# 交叉表
df_crosstab = pd.crosstab(df['category1'], df['category2'])
```

## 7. 数据清洗

### 7.1 缺失值处理

```python
# 检查缺失值
df.isnull()
df.isna()
df.isnull().sum()

# 删除缺失值
df.dropna()              # 删除包含缺失值的行
df.dropna(axis=1)        # 删除包含缺失值的列
df.dropna(subset=['列名'])  # 删除指定列的缺失值

# 填充缺失值
df.fillna(0)             # 用0填充
df.fillna(method='ffill') # 前向填充
df.fillna(method='bfill') # 后向填充
df.fillna(df.mean())     # 用均值填充
```

### 7.2 重复值处理

```python
# 检查重复值
df.duplicated()

# 删除重复值
df.drop_duplicates()
df.drop_duplicates(subset=['列名'])
```

### 7.3 异常值处理

```python
# 使用3σ原则
mean = df['列名'].mean()
std = df['列名'].std()
df = df[(df['列名'] >= mean - 3*std) & (df['列名'] <= mean + 3*std)]

# 使用IQR方法
Q1 = df['列名'].quantile(0.25)
Q3 = df['列名'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['列名'] >= Q1 - 1.5*IQR) & (df['列名'] <= Q3 + 1.5*IQR)]
```

## 8. 数据预处理

### 8.1 数据类型转换

```python
# 转换数据类型
df['列名'] = df['列名'].astype('int64')
df['列名'] = pd.to_numeric(df['列名'])
df['列名'] = pd.to_datetime(df['列名'])
```

### 8.2 数据变换

```python
# 标准化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df['列名'] = scaler.fit_transform(df[['列名']])

# 归一化
df['列名'] = (df['列名'] - df['列名'].min()) / (df['列名'].max() - df['列名'].min())
```

## 9. 数据透视和分析

### 9.1 描述性统计

```python
# 基本统计
df.mean()      # 均值
df.median()    # 中位数
df.std()       # 标准差
df.var()       # 方差
df.min()       # 最小值
df.max()       # 最大值
df.sum()       # 总和

# 综合统计
df.describe()
```

### 9.2 分组聚合

```python
# 分组
df.groupby('列名')

# 分组聚合
df.groupby('列名').mean()
df.groupby('列名').sum()
df.groupby('列名').agg({'列1': 'mean', '列2': 'sum'})

# 多列分组
df.groupby(['列1', '列2']).mean()
```

### 9.3 排序

```python
# 单列排序
df.sort_values('列名')

# 多列排序
df.sort_values(['列1', '列2'], ascending=[True, False])

# 按索引排序
df.sort_index()
```

### 9.4 排名

```python
df['排名'] = df['列名'].rank(ascending=False)
```

## 10. 时间序列处理

### 10.1 时间索引

```python
# 创建时间索引
dates = pd.date_range('2023-01-01', periods=365, freq='D')
df = pd.DataFrame(data, index=dates)

# 时间索引操作
df['2023-01']           # 选择2023年1月
df['2023-01-01':'2023-01-31']  # 时间范围
```

### 10.2 时间重采样

```python
# 按天重采样为月
df.resample('M').mean()

# 按周重采样
df.resample('W').sum()
```

## 11. 数据写入

### 11.1 写入CSV文件

```python
df.to_csv('output.csv', index=False)
```

### 11.2 写入Excel文件

```python
df.to_excel('output.xlsx', sheet_name='Sheet1', index=False)
```

### 11.3 写入数据库

```python
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://user:password@localhost/dbname')
df.to_sql('table_name', engine, if_exists='replace', index=False)
```

## 12. 高级功能

### 12.1 窗口函数

```python
# 移动平均
df['MA5'] = df['列名'].rolling(window=5).mean()

# 累计和
df['累计'] = df['列名'].cumsum()
```

### 12.2 数据转换

```python
# apply方法
df['新列'] = df['列名'].apply(lambda x: x * 2)

# map方法
df['新列'] = df['列名'].map({1: 'A', 2: 'B', 3: 'C'})

# replace方法
df['列名'].replace({1: 'A', 2: 'B'})
```

### 12.3 数据透视表

```python
df_pivot = pd.pivot_table(df, 
                          values='value',
                          index='row',
                          columns='col',
                          aggfunc='mean')
```

## 13. 性能优化

### 13.1 使用合适的数据类型

```python
# 将object类型转换为category类型
df['列名'] = df['列名'].astype('category')
```

### 13.2 使用向量化操作

```python
# 好的做法：向量化操作
df['新列'] = df['列1'] + df['列2']

# 避免：循环操作
# for i in range(len(df)):
#     df.loc[i, '新列'] = df.loc[i, '列1'] + df.loc[i, '列2']
```

## 14. 常用技巧

### 14.1 数据采样

```python
# 随机采样
df.sample(n=10)
df.sample(frac=0.1)  # 10%的样本
```

### 14.2 数据筛选

```python
# 使用isin
df[df['列名'].isin([值1, 值2, 值3])]

# 使用contains
df[df['列名'].str.contains('关键词')]
```

### 14.3 数据分组应用

```python
# 分组后应用函数
df.groupby('列名').apply(lambda x: x.sort_values('另一列'))
```

## 15. 总结

Pandas 是 Python 数据分析的核心库，提供了强大的数据处理和分析功能。掌握 Pandas 的 Series 和 DataFrame 操作、数据清洗、数据透视、分组聚合等功能，是进行数据分析的基础。Pandas 与 NumPy、Matplotlib 等库的配合使用，可以完成从数据获取到数据可视化的完整数据分析流程。

