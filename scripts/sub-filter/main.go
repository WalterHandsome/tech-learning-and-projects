package main

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/sub-filter/internal/config"
	"github.com/sub-filter/internal/encoder"
	"github.com/sub-filter/internal/model"
	"github.com/sub-filter/internal/operator"
	"github.com/sub-filter/internal/parser"
	"github.com/sub-filter/internal/pipeline"
	"github.com/sub-filter/internal/source"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	configPath := "config.yaml"
	if len(os.Args) > 2 {
		configPath = os.Args[2]
	}

	switch cmd {
	case "run":
		runFull(configPath)
	case "inspect":
		runInspect(configPath)
	case "clean":
		runClean()
	case "help":
		printUsage()
	default:
		fmt.Printf("❌ 未知命令: %s\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println(`sub-filter - V2Ray 订阅过滤器

用法:
  sub-filter run [config.yaml]      完整流程：下载→过滤→测速→采样→输出
  sub-filter inspect [config.yaml]  只下载解析，查看统计信息
  sub-filter clean                  清除缓存
  sub-filter help                   显示帮助`)
}

func runFull(configPath string) {
	startTime := time.Now()

	// 加载配置
	cfg, err := config.Load(configPath)
	if err != nil {
		fmt.Printf("❌ 加载配置失败: %v\n", err)
		os.Exit(1)
	}

	// 下载并合并所有订阅
	var allNodes []model.Node
	totalFail := 0
	for _, sub := range cfg.Subscriptions {
		fmt.Printf("📥 下载订阅: %s\n", truncateURL(sub.URL))
		content, err := source.Download(sub.URL, sub.UserAgent)
		if err != nil {
			fmt.Printf("   ❌ 下载失败: %v\n", err)
			continue
		}
		nodes, failCount := parser.ParseSubscription(content)
		fmt.Printf("   ✅ 解析成功: %d 个节点（%d 个失败）\n", len(nodes), failCount)
		allNodes = append(allNodes, nodes...)
		totalFail += failCount
	}

	if len(allNodes) == 0 {
		fmt.Println("❌ 没有解析到任何节点")
		os.Exit(1)
	}

	fmt.Printf("\n📊 原始节点总数: %d\n\n", len(allNodes))

	// 执行管道
	progressFn := func(done, total int) {
		pct := float64(done) / float64(total) * 100
		fmt.Printf("\r🏓 测速中... %d/%d (%.1f%%)", done, total, pct)
	}

	result, steps, regionGroups := pipeline.Run(allNodes, cfg.Pipeline, progressFn)

	// 打印管道步骤结果
	fmt.Println("\n")
	fmt.Println("📋 管道执行结果:")
	fmt.Println(strings.Repeat("─", 50))
	for _, s := range steps {
		fmt.Printf("   %-16s %d → %d\n", s.Name, s.InputCount, s.OutputCount)
	}
	fmt.Println(strings.Repeat("─", 50))

	// 打印地区分布
	if len(regionGroups) > 0 {
		fmt.Println("\n🌏 地区分布:")
		fmt.Println(strings.Repeat("─", 50))
		for _, g := range regionGroups {
			minLatency := float64(0)
			if len(g.Nodes) > 0 {
				minLatency = g.Nodes[0].Latency
			}
			fmt.Printf("   %-16s %3d 个节点  最低延迟: %.0fms\n", g.Name, len(g.Nodes), minLatency)
		}
		fmt.Println(strings.Repeat("─", 50))
	}

	// 输出
	if err := encoder.Encode(result, cfg.Output.File, cfg.Output.Format); err != nil {
		fmt.Printf("❌ 输出失败: %v\n", err)
		os.Exit(1)
	}

	elapsed := time.Since(startTime)
	fmt.Printf("\n💾 输出到: %s (%d 个节点)\n", cfg.Output.File, len(result))
	fmt.Printf("⏱️  总耗时: %s\n", formatDuration(elapsed))
}

func runInspect(configPath string) {
	cfg, err := config.Load(configPath)
	if err != nil {
		fmt.Printf("❌ 加载配置失败: %v\n", err)
		os.Exit(1)
	}

	for _, sub := range cfg.Subscriptions {
		fmt.Printf("📥 下载订阅: %s\n", truncateURL(sub.URL))
		content, err := source.Download(sub.URL, sub.UserAgent)
		if err != nil {
			fmt.Printf("   ❌ 下载失败: %v\n", err)
			continue
		}
		nodes, failCount := parser.ParseSubscription(content)
		fmt.Printf("   ✅ 解析成功: %d 个节点（%d 个失败）\n\n", len(nodes), failCount)

		// 统计协议分布
		protocolCount := make(map[string]int)
		for _, n := range nodes {
			protocolCount[n.Protocol]++
		}
		fmt.Println("📊 协议分布:")
		for proto, count := range protocolCount {
			fmt.Printf("   %-10s %d\n", proto, count)
		}

		// 统计地区分布（取前 20）
		regionCount := make(map[string]int)
		for _, n := range nodes {
			region := operator.MatchRegion(n.Name)
			regionCount[region]++
		}
		fmt.Println("\n🌏 地区分布:")
		for region, count := range regionCount {
			fmt.Printf("   %-16s %d\n", region, count)
		}
	}
}

func runClean() {
	if err := os.RemoveAll(".cache"); err != nil {
		fmt.Printf("❌ 清除缓存失败: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("✅ 缓存已清除")
}

func truncateURL(u string) string {
	if len(u) > 60 {
		return u[:60] + "..."
	}
	return u
}

func formatDuration(d time.Duration) string {
	if d < time.Minute {
		return fmt.Sprintf("%.1f 秒", d.Seconds())
	}
	m := int(d.Minutes())
	s := int(d.Seconds()) % 60
	return fmt.Sprintf("%d 分 %d 秒", m, s)
}