package encoder

import (
	"encoding/base64"
	"os"
	"strings"

	"github.com/sub-filter/internal/model"
)

// Encode 将节点列表编码为订阅内容并写入文件
func Encode(nodes []model.Node, outputFile string, format string) error {
	var lines []string
	for _, n := range nodes {
		if n.RawLink != "" {
			lines = append(lines, n.RawLink)
		}
	}
	content := strings.Join(lines, "\n")

	if format == "base64" {
		content = base64.StdEncoding.EncodeToString([]byte(content))
	}

	return os.WriteFile(outputFile, []byte(content), 0644)
}
