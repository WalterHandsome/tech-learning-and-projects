package operator

import (
	"regexp"

	"github.com/sub-filter/internal/model"
)

// RegexFilter 正则过滤
// action="exclude": 匹配的排除
// action="include": 匹配的保留
func RegexFilter(nodes []model.Node, pattern string, action string) []model.Node {
	re, err := regexp.Compile("(?i)" + pattern)
	if err != nil {
		// 正则编译失败，返回原列表
		return nodes
	}

	var result []model.Node
	for _, n := range nodes {
		matched := re.MatchString(n.Name)
		if action == "exclude" && !matched {
			result = append(result, n)
		} else if action == "include" && matched {
			result = append(result, n)
		}
	}
	return result
}

// TypeFilter 按协议类型过滤
func TypeFilter(nodes []model.Node, allow []string) []model.Node {
	if len(allow) == 0 {
		return nodes
	}
	allowMap := make(map[string]bool)
	for _, t := range allow {
		allowMap[t] = true
	}
	var result []model.Node
	for _, n := range nodes {
		if allowMap[n.Protocol] {
			result = append(result, n)
		}
	}
	return result
}
