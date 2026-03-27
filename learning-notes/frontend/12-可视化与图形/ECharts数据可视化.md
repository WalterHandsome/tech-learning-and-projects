# ECharts 数据可视化

> Author: Walter Wang

## 1. 基本使用

```javascript
import * as echarts from 'echarts';

const chart = echarts.init(document.getElementById('chart'));

chart.setOption({
  title: { text: '销售数据' },
  tooltip: { trigger: 'axis' },
  legend: { data: ['销量', '利润'] },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月'] },
  yAxis: { type: 'value' },
  series: [
    { name: '销量', type: 'bar', data: [120, 200, 150, 80, 70] },
    { name: '利润', type: 'line', data: [50, 80, 60, 30, 25] },
  ],
});

// 响应式
window.addEventListener('resize', () => chart.resize());
```

## 2. 常用图表

```javascript
// 饼图
{
  series: [{
    type: 'pie',
    radius: ['40%', '70%'], // 环形图
    data: [
      { value: 1048, name: '搜索引擎' },
      { value: 735, name: '直接访问' },
      { value: 580, name: '邮件营销' },
    ],
  }],
}

// 散点图
{
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    type: 'scatter',
    symbolSize: (data) => Math.sqrt(data[2]) * 5,
    data: [[10, 8, 100], [20, 15, 200], [30, 25, 300]],
  }],
}
```

## 3. React/Vue 集成

```jsx
// React（使用 echarts-for-react）
import ReactECharts from 'echarts-for-react';

function Chart({ data }) {
  const option = {
    xAxis: { type: 'category', data: data.map(d => d.name) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: data.map(d => d.value) }],
  };
  return <ReactECharts option={option} style={{ height: 400 }} />;
}
```

## 4. 大数据量优化

```javascript
chart.setOption({
  dataset: { source: largeData },
  series: [{
    type: 'scatter',
    large: true,           // 开启大数据量优化
    largeThreshold: 2000,  // 阈值
    progressive: 400,      // 渐进渲染
    progressiveThreshold: 3000,
  }],
});
```
