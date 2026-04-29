package parser

import (
	"encoding/json"
	"fmt"
	"net/url"
	"strconv"
	"strings"

	"github.com/sub-filter/internal/model"
)

// ParseSubscription 解析订阅内容，返回节点列表和失败数
func ParseSubscription(content string) ([]model.Node, int) {
	// 尝试 Base64 解码
	decoded, err := decodeBase64(content)
	if err == nil && len(decoded) > 0 {
		content = decoded
	}

	lines := strings.Split(strings.TrimSpace(content), "\n")
	var nodes []model.Node
	failCount := 0

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		node, err := parseLine(line)
		if err != nil {
			failCount++
			continue
		}
		nodes = append(nodes, node)
	}
	return nodes, failCount
}

// parseLine 解析单行节点链接
func parseLine(line string) (model.Node, error) {
	switch {
	case strings.HasPrefix(line, "vmess://"):
		return parseVMess(line)
	case strings.HasPrefix(line, "vless://"):
		return parseVLESS(line)
	case strings.HasPrefix(line, "trojan://"):
		return parseTrojan(line)
	case strings.HasPrefix(line, "ss://"):
		return parseSS(line)
	case strings.HasPrefix(line, "ssr://"):
		return parseSSR(line)
	default:
		return model.Node{}, fmt.Errorf("不支持的协议: %s", truncate(line, 30))
	}
}

// parseVMess 解析 vmess:// 链接 (vmess://base64(json))
func parseVMess(link string) (model.Node, error) {
	raw := strings.TrimPrefix(link, "vmess://")
	decoded, err := decodeBase64(raw)
	if err != nil {
		return model.Node{}, fmt.Errorf("vmess base64 解码失败: %w", err)
	}
	var obj map[string]interface{}
	if err := json.Unmarshal([]byte(decoded), &obj); err != nil {
		return model.Node{}, fmt.Errorf("vmess json 解析失败: %w", err)
	}
	port, _ := toInt(obj["port"])
	name, _ := obj["ps"].(string)
	if name == "" {
		name, _ = obj["remarks"].(string)
	}
	addr, _ := obj["add"].(string)
	if addr == "" || port == 0 {
		return model.Node{}, fmt.Errorf("vmess 缺少 addr 或 port")
	}
	return model.Node{
		Name: name, Addr: addr, Port: port,
		Protocol: "vmess", RawLink: link, Latency: -1, Alive: true,
	}, nil
}

// parseVLESS 解析 vless://uuid@host:port?params#name
func parseVLESS(link string) (model.Node, error) {
	return parseURIStyle(link, "vless")
}

// parseTrojan 解析 trojan://password@host:port?params#name
func parseTrojan(link string) (model.Node, error) {
	return parseURIStyle(link, "trojan")
}

// parseURIStyle 解析 URI 风格的链接（vless/trojan 通用）
func parseURIStyle(link string, protocol string) (model.Node, error) {
	u, err := url.Parse(link)
	if err != nil {
		return model.Node{}, fmt.Errorf("%s URL 解析失败: %w", protocol, err)
	}
	host := u.Hostname()
	portStr := u.Port()
	port, _ := strconv.Atoi(portStr)
	name, _ := url.PathUnescape(u.Fragment)
	path := u.Query().Get("path")
	if host == "" || port == 0 {
		return model.Node{}, fmt.Errorf("%s 缺少 host 或 port", protocol)
	}
	return model.Node{
		Name: name, Addr: host, Port: port, Path: path,
		Protocol: protocol, RawLink: link, Latency: -1, Alive: true,
	}, nil
}
