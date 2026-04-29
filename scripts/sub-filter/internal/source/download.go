package source

import (
	"fmt"
	"io"
	"net/http"
	neturl "net/url"
	"os"
	"strings"
	"time"
)

// Download 下载订阅内容
func Download(url string, userAgent string) (string, error) {
	// 本地文件
	if strings.HasPrefix(url, "file://") {
		path := strings.TrimPrefix(url, "file://")
		data, err := os.ReadFile(path)
		if err != nil {
			return "", fmt.Errorf("读取本地文件失败: %w", err)
		}
		return string(data), nil
	}

	if userAgent == "" {
		userAgent = "v2ray"
	}

	client := &http.Client{Timeout: 60 * time.Second}

	// 自动检测代理：HTTP_PROXY / HTTPS_PROXY / ALL_PROXY 环境变量
	proxyURL := os.Getenv("HTTPS_PROXY")
	if proxyURL == "" {
		proxyURL = os.Getenv("HTTP_PROXY")
	}
	if proxyURL == "" {
		proxyURL = os.Getenv("ALL_PROXY")
	}
	if proxyURL != "" {
		if parsed, err := neturl.Parse(proxyURL); err == nil {
			client.Transport = &http.Transport{
				Proxy: http.ProxyURL(parsed),
			}
			fmt.Printf("   🔗 使用代理: %s\n", proxyURL)
		}
	}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %w", err)
	}
	req.Header.Set("User-Agent", userAgent)

	var lastErr error
	// 重试 3 次
	for i := 0; i < 3; i++ {
		resp, err := client.Do(req)
		if err != nil {
			lastErr = err
			time.Sleep(2 * time.Second)
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			lastErr = fmt.Errorf("HTTP %d", resp.StatusCode)
			time.Sleep(2 * time.Second)
			continue
		}

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			lastErr = fmt.Errorf("读取响应失败: %w", err)
			time.Sleep(2 * time.Second)
			continue
		}
		return string(body), nil
	}
	return "", fmt.Errorf("下载失败（重试3次）: %w", lastErr)
}
