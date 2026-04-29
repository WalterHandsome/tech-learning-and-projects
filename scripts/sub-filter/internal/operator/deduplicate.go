package operator

import "github.com/sub-filter/internal/model"

// Deduplicate 按 addr:port 去重，保留第一个
func Deduplicate(nodes []model.Node) []model.Node {
	seen := make(map[string]bool)
	var result []model.Node
	for _, n := range nodes {
		key := n.Key()
		if seen[key] {
			continue
		}
		seen[key] = true
		result = append(result, n)
	}
	return result
}
