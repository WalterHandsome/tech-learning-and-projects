package parser

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/url"
	"strconv"
	"strings"

	"github.com/sub-filter/internal/model"
)

// parseSS 解析 ss:// 链接
// 格式1: ss://base64(method:password)@host:port#name
// 格式2: ss://base64(method:password@host:port)#name
func parseSS(link string) (model.Node, error) {
	raw := strings.TrimPrefix(link, "ss://")
	name := ""
	if idx := strings.LastIndex(raw, "#"); idx != -1 {
		name, _ = url.PathUnescape(raw[idx+1:])
		raw = raw[:idx]
	}
	// 格式1: base64部分@host:port
	if idx := strings.LastIndex(raw, "@"); idx != -1 {
		hostPort := raw[idx+1:]
		host, portStr, err := splitHostPort(hostPort)
		if err != nil {
			return model.Node{}, fmt.Errorf("ss 解析 host:port 失败: %w", err)
		}
		port, _ := strconv.Atoi(portStr)
		return model.Node{
			Name: name, Addr: host, Port: port,
			Protocol: "ss", RawLink: link, Latency: -1, Alive: true,
		}, nil
	}
	// 格式2: 整体 base64
	decoded, err := decodeBase64(raw)
	if err != nil {
		return model.Node{}, fmt.Errorf("ss base64 解码失败: %w", err)
	}
	if idx := strings.LastIndex(decoded, "@"); idx != -1 {
		hostPort := decoded[idx+1:]
		host, portStr, err := splitHostPort(hostPort)
		if err != nil {
			return model.Node{}, fmt.Errorf("ss 解析 host:port 失败: %w", err)
		}
		port, _ := strconv.Atoi(portStr)
		return model.Node{
			Name: name, Addr: host, Port: port,
			Protocol: "ss", RawLink: link, Latency: -1, Alive: true,
		}, nil
	}
	return model.Node{}, fmt.Errorf("ss 格式无法识别")
}

// parseSSR 解析 ssr:// 链接
// ssr://base64(host:port:protocol:method:obfs:base64pass/?params)
func parseSSR(link string) (model.Node, error) {
	raw := strings.TrimPrefix(link, "ssr://")
	decoded, err := decodeBase64(raw)
	if err != nil {
		return model.Node{}, fmt.Errorf("ssr base64 解码失败: %w", err)
	}
	// 提取 remarks 参数作为名称
	name := ""
	if idx := strings.Index(decoded, "/?"); idx != -1 {
		params := decoded[idx+2:]
		decoded = decoded[:idx]
		for _, param := range strings.Split(params, "&") {
			kv := strings.SplitN(param, "=", 2)
			if len(kv) == 2 && kv[0] == "remarks" {
				remarksDecoded, err := decodeBase64(kv[1])
				if err == nil {
					name = remarksDecoded
				}
			}
		}
	}
	// host:port:protocol:method:obfs:base64pass
	parts := strings.SplitN(decoded, ":", 6)
	if len(parts) < 2 {
		return model.Node{}, fmt.Errorf("ssr 格式无法识别")
	}
	host := parts[0]
	port, _ := strconv.Atoi(parts[1])
	if host == "" || port == 0 {
		return model.Node{}, fmt.Errorf("ssr 缺少 host 或 port")
	}
	return model.Node{
		Name: name, Addr: host, Port: port,
		Protocol: "ssr", RawLink: link, Latency: -1, Alive: true,
	}, nil
}

// decodeBase64 尝试多种 Base64 变体解码
func decodeBase64(s string) (string, error) {
	s = strings.TrimSpace(s)
	// 补齐 padding
	if m := len(s) % 4; m != 0 {
		s += strings.Repeat("=", 4-m)
	}
	// 标准 Base64
	if decoded, err := base64.StdEncoding.DecodeString(s); err == nil {
		return string(decoded), nil
	}
	// URL-safe Base64
	if decoded, err := base64.URLEncoding.DecodeString(s); err == nil {
		return string(decoded), nil
	}
	// 去掉 padding 再试 RawStdEncoding
	s = strings.TrimRight(s, "=")
	if decoded, err := base64.RawStdEncoding.DecodeString(s); err == nil {
		return string(decoded), nil
	}
	if decoded, err := base64.RawURLEncoding.DecodeString(s); err == nil {
		return string(decoded), nil
	}
	return "", fmt.Errorf("base64 解码失败")
}

// splitHostPort 分割 host:port，处理 IPv6
func splitHostPort(hostPort string) (string, string, error) {
	// IPv6: [::1]:443
	if strings.HasPrefix(hostPort, "[") {
		end := strings.Index(hostPort, "]")
		if end == -1 {
			return "", "", fmt.Errorf("无效的 IPv6 地址")
		}
		host := hostPort[1:end]
		if end+1 < len(hostPort) && hostPort[end+1] == ':' {
			return host, hostPort[end+2:], nil
		}
		return host, "", nil
	}
	parts := strings.SplitN(hostPort, ":", 2)
	if len(parts) != 2 {
		return "", "", fmt.Errorf("无效的 host:port 格式")
	}
	return parts[0], parts[1], nil
}

// toInt 将 interface{} 转为 int
func toInt(v interface{}) (int, error) {
	switch val := v.(type) {
	case float64:
		return int(val), nil
	case string:
		return strconv.Atoi(val)
	case int:
		return val, nil
	case json.Number:
		i, err := val.Int64()
		return int(i), err
	default:
		return 0, fmt.Errorf("无法转换为 int: %v", v)
	}
}

// truncate 截断字符串
func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}
