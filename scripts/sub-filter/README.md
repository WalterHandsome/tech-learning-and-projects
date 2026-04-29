# Sub-Filter - V2Ray 订阅过滤器

将海量代理节点订阅（如 17 万个）精简为几百个可用节点，方便导入手机客户端。

## 功能

- 支持 vmess/vless/trojan/ss/ssr 五种协议解析
- 管道架构：去重 → 正则过滤 → TCP 测速 → 地区采样，可自由组合
- 并发 TCP 测速（goroutine，200 并发）
- 内置 43 个国家/地区识别，每个地区取延迟最低的 Top N
- YAML 配置，不用改代码

## 使用

```bash
# 编译
go build -o sub-filter .

# 编辑配置（修改订阅链接）
vim config.yaml

# 运行完整流程
./sub-filter run

# 只查看统计信息（不测速不输出）
./sub-filter inspect

# 清除缓存
./sub-filter clean
```

## 配置说明

见 `config.yaml` 中的注释。

## 管道算子

| 算子 | 说明 |
|------|------|
| `deduplicate` | 按 addr:port 去重 |
| `regex_filter` | 正则过滤（include/exclude） |
| `type_filter` | 按协议类型过滤 |
| `health_check` | TCP 延迟测速 |
| `region_sample` | 地区分组 + 采样 |
