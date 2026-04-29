package model

import (
	"fmt"
	"time"
)

// Node 表示一个代理节点
type Node struct {
	Name     string  // 节点名称
	Addr     string  // 服务器地址
	Port     int     // 端口
	Path     string  // 路径（用于区分 CF Workers 节点）
	Protocol string  // 协议类型: vmess/vless/trojan/ss/ssr
	RawLink  string  // 原始链接（用于输出）
	Region   string  // 地区（由 region_sample 算子填充）
	Latency  float64 // 延迟毫秒（由 health_check 算子填充，-1=未测）
	Alive    bool    // 是否存活
	Speed    float64 // 下载速度 KB/s（可选测速填充，0=未测）
}

// Key 返回去重用的唯一标识
// 对于 CF Workers 节点，path 不同代表不同的后端服务器
func (n *Node) Key() string {
	if n.Path != "" {
		return fmt.Sprintf("%s:%d:%s", n.Addr, n.Port, n.Path)
	}
	return fmt.Sprintf("%s:%d", n.Addr, n.Port)
}

// CacheEntry 缓存条目
type CacheEntry struct {
	Nodes     []Node    `json:"nodes"`
	CreatedAt time.Time `json:"created_at"`
	ConfigMD5 string    `json:"config_md5"`
}

// SpeedCacheEntry 测速缓存条目
type SpeedCacheEntry struct {
	Results   map[string]SpeedResult `json:"results"` // key: addr:port
	CreatedAt time.Time              `json:"created_at"`
}

// SpeedResult 单个节点的测速结果
type SpeedResult struct {
	Latency float64 `json:"latency"` // 毫秒
	Alive   bool    `json:"alive"`
	Speed   float64 `json:"speed"` // KB/s
}
