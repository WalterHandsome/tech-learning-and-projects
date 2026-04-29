package operator

import (
	"fmt"
	"net"
	"sync"
	"sync/atomic"
	"time"

	"github.com/sub-filter/internal/model"
)

// HealthCheckResult 测速结果
type HealthCheckResult struct {
	Index   int
	Latency float64 // 毫秒，-1 表示失败
	Alive   bool
}

// TCPHealthCheck 并发 TCP 延迟测试
func TCPHealthCheck(nodes []model.Node, concurrency int, timeout int, progressFn func(done, total int)) []model.Node {
	if concurrency <= 0 {
		concurrency = 200
	}
	if timeout <= 0 {
		timeout = 3
	}

	total := len(nodes)
	results := make([]HealthCheckResult, total)
	var done int64

	sem := make(chan struct{}, concurrency)
	var wg sync.WaitGroup

	for i, n := range nodes {
		wg.Add(1)
		sem <- struct{}{}
		go func(idx int, node model.Node) {
			defer wg.Done()
			defer func() { <-sem }()

			addr := fmt.Sprintf("%s:%d", node.Addr, node.Port)
			start := time.Now()
			conn, err := net.DialTimeout("tcp", addr, time.Duration(timeout)*time.Second)
			elapsed := time.Since(start).Seconds() * 1000 // 毫秒

			if err != nil {
				results[idx] = HealthCheckResult{Index: idx, Latency: -1, Alive: false}
			} else {
				conn.Close()
				results[idx] = HealthCheckResult{Index: idx, Latency: elapsed, Alive: true}
			}

			current := atomic.AddInt64(&done, 1)
			if progressFn != nil {
				progressFn(int(current), total)
			}
		}(i, n)
	}
	wg.Wait()

	// 应用结果
	var alive []model.Node
	for i, r := range results {
		if r.Alive {
			nodes[i].Latency = r.Latency
			nodes[i].Alive = true
			alive = append(alive, nodes[i])
		}
	}
	return alive
}
