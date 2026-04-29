package pipeline

import (
	"fmt"

	"github.com/sub-filter/internal/config"
	"github.com/sub-filter/internal/model"
	"github.com/sub-filter/internal/operator"
)

// StepResult 单步执行结果
type StepResult struct {
	Name        string
	InputCount  int
	OutputCount int
}

// ProgressFn 进度回调
type ProgressFn func(done, total int)

// Run 执行管道
func Run(nodes []model.Node, ops []config.Operator, progressFn ProgressFn) ([]model.Node, []StepResult, []operator.RegionGroup) {
	var results []StepResult
	var regionGroups []operator.RegionGroup

	for _, op := range ops {
		inputCount := len(nodes)
		stepName := op.Type

		switch op.Type {
		case "deduplicate":
			nodes = operator.Deduplicate(nodes)

		case "regex_filter":
			nodes = operator.RegexFilter(nodes, op.Pattern, op.Action)

		case "type_filter":
			nodes = operator.TypeFilter(nodes, op.Allow)

		case "health_check":
			concurrency := op.TCP.Concurrency
			timeout := op.TCP.Timeout
			if concurrency == 0 {
				concurrency = 200
			}
			if timeout == 0 {
				timeout = 3
			}
			nodes = operator.TCPHealthCheck(nodes, concurrency, timeout, progressFn)

		case "region_sample":
			perRegion := op.PerRegion
			if perRegion == 0 {
				perRegion = 20
			}
			nodes, regionGroups = operator.RegionSample(nodes, perRegion, op.SortBy)

		default:
			fmt.Printf("⚠️  未知算子: %s，跳过\n", op.Type)
			continue
		}

		results = append(results, StepResult{
			Name:        stepName,
			InputCount:  inputCount,
			OutputCount: len(nodes),
		})
	}

	return nodes, results, regionGroups
}
