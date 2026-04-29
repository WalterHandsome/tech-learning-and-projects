package operator

import (
	"sort"
	"strings"

	"github.com/sub-filter/internal/model"
)

// RegionDef 地区定义
type RegionDef struct {
	Name     string
	Keywords []string
}

// DefaultRegions 内置地区映射表
var DefaultRegions = []RegionDef{
	{Name: "🇭🇰 香港", Keywords: []string{"HK", "香港", "Hong Kong", "Hongkong"}},
	{Name: "🇯🇵 日本", Keywords: []string{"JP", "日本", "Japan", "Tokyo", "Osaka"}},
	{Name: "🇺🇸 美国", Keywords: []string{"US", "美国", "United States", "America", "Los Angeles", "San Jose", "Seattle", "New York"}},
	{Name: "🇸🇬 新加坡", Keywords: []string{"SG", "新加坡", "Singapore"}},
	{Name: "🇰🇷 韩国", Keywords: []string{"KR", "韩国", "Korea", "Seoul"}},
	{Name: "🇹🇼 台湾", Keywords: []string{"TW", "台湾", "Taiwan"}},
	{Name: "🇬🇧 英国", Keywords: []string{"UK", "GB", "英国", "United Kingdom", "London", "England"}},
	{Name: "🇩🇪 德国", Keywords: []string{"DE", "德国", "Germany", "Frankfurt"}},
	{Name: "🇫🇷 法国", Keywords: []string{"FR", "法国", "France", "Paris"}},
	{Name: "🇳🇱 荷兰", Keywords: []string{"NL", "荷兰", "Netherlands", "Amsterdam"}},
	{Name: "🇨🇦 加拿大", Keywords: []string{"CA", "加拿大", "Canada", "Toronto", "Montreal"}},
	{Name: "🇦🇺 澳大利亚", Keywords: []string{"AU", "澳大利亚", "Australia", "Sydney", "Melbourne"}},
	{Name: "🇷🇺 俄罗斯", Keywords: []string{"RU", "俄罗斯", "Russia", "Moscow"}},
	{Name: "🇮🇳 印度", Keywords: []string{"IN", "印度", "India", "Mumbai"}},
	{Name: "🇧🇷 巴西", Keywords: []string{"BR", "巴西", "Brazil"}},
	{Name: "🇹🇷 土耳其", Keywords: []string{"TR", "土耳其", "Turkey", "Türkiye", "Istanbul"}},
	{Name: "🇦🇷 阿根廷", Keywords: []string{"AR", "阿根廷", "Argentina"}},
	{Name: "🇮🇹 意大利", Keywords: []string{"IT", "意大利", "Italy"}},
	{Name: "🇪🇸 西班牙", Keywords: []string{"ES", "西班牙", "Spain"}},
	{Name: "🇵🇱 波兰", Keywords: []string{"PL", "波兰", "Poland"}},
	{Name: "🇫🇮 芬兰", Keywords: []string{"FI", "芬兰", "Finland", "Helsinki"}},
	{Name: "🇸🇪 瑞典", Keywords: []string{"SE", "瑞典", "Sweden"}},
	{Name: "🇳🇴 挪威", Keywords: []string{"NO", "挪威", "Norway"}},
	{Name: "🇩🇰 丹麦", Keywords: []string{"DK", "丹麦", "Denmark"}},
	{Name: "🇨🇭 瑞士", Keywords: []string{"CH", "瑞士", "Switzerland", "Zurich"}},
	{Name: "🇦🇹 奥地利", Keywords: []string{"AT", "奥地利", "Austria", "Vienna"}},
	{Name: "🇮🇪 爱尔兰", Keywords: []string{"IE", "爱尔兰", "Ireland", "Dublin"}},
	{Name: "🇵🇹 葡萄牙", Keywords: []string{"PT", "葡萄牙", "Portugal"}},
	{Name: "🇬🇷 希腊", Keywords: []string{"GR", "希腊", "Greece"}},
	{Name: "🇷🇴 罗马尼亚", Keywords: []string{"RO", "罗马尼亚", "Romania"}},
	{Name: "🇺🇦 乌克兰", Keywords: []string{"UA", "乌克兰", "Ukraine"}},
	{Name: "🇮🇱 以色列", Keywords: []string{"IL", "以色列", "Israel"}},
	{Name: "🇿🇦 南非", Keywords: []string{"ZA", "南非", "South Africa"}},
	{Name: "🇲🇽 墨西哥", Keywords: []string{"MX", "墨西哥", "Mexico"}},
	{Name: "🇨🇱 智利", Keywords: []string{"CL", "智利", "Chile"}},
	{Name: "🇨🇴 哥伦比亚", Keywords: []string{"CO", "哥伦比亚", "Colombia"}},
	{Name: "🇹🇭 泰国", Keywords: []string{"TH", "泰国", "Thailand", "Bangkok"}},
	{Name: "🇻🇳 越南", Keywords: []string{"VN", "越南", "Vietnam"}},
	{Name: "🇵🇭 菲律宾", Keywords: []string{"PH", "菲律宾", "Philippines"}},
	{Name: "🇮🇩 印尼", Keywords: []string{"ID", "印尼", "印度尼西亚", "Indonesia", "Jakarta"}},
	{Name: "🇲🇾 马来西亚", Keywords: []string{"MY", "马来西亚", "Malaysia"}},
	{Name: "🇰🇿 哈萨克斯坦", Keywords: []string{"KZ", "哈萨克", "Kazakhstan"}},
	{Name: "🇦🇪 阿联酋", Keywords: []string{"AE", "阿联酋", "UAE", "Dubai"}},
}

// MatchRegion 匹配节点所属地区
func MatchRegion(name string) string {
	upper := strings.ToUpper(name)
	for _, r := range DefaultRegions {
		for _, kw := range r.Keywords {
			if strings.Contains(upper, strings.ToUpper(kw)) {
				return r.Name
			}
		}
	}
	return "🌍 其他"
}

// RegionGroup 地区分组结果
type RegionGroup struct {
	Name  string
	Nodes []model.Node
}

// RegionSample 地区分组 + 每组取延迟最低的 Top N
func RegionSample(nodes []model.Node, perRegion int, sortBy string) ([]model.Node, []RegionGroup) {
	if perRegion <= 0 {
		perRegion = 20
	}

	// 分配地区
	for i := range nodes {
		nodes[i].Region = MatchRegion(nodes[i].Name)
	}

	// 分组
	groupMap := make(map[string][]model.Node)
	for _, n := range nodes {
		groupMap[n.Region] = append(groupMap[n.Region], n)
	}

	// 每组排序 + 取 Top N
	var result []model.Node
	var groups []RegionGroup
	for regionName, regionNodes := range groupMap {
		// 按延迟排序
		if sortBy == "latency" {
			sort.Slice(regionNodes, func(i, j int) bool {
				return regionNodes[i].Latency < regionNodes[j].Latency
			})
		}
		kept := regionNodes
		if len(kept) > perRegion {
			kept = kept[:perRegion]
		}
		result = append(result, kept...)
		groups = append(groups, RegionGroup{Name: regionName, Nodes: kept})
	}

	// 按地区名排序（输出稳定）
	sort.Slice(groups, func(i, j int) bool {
		return groups[i].Name < groups[j].Name
	})

	return result, groups
}
