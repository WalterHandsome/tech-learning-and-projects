package config

import (
	"os"

	"gopkg.in/yaml.v3"
)

// Config 应用配置
type Config struct {
	Subscriptions []Subscription `yaml:"subscriptions"`
	Pipeline      []Operator     `yaml:"pipeline"`
	Output        Output         `yaml:"output"`
	Cache         CacheConfig    `yaml:"cache"`
}

// Subscription 订阅源
type Subscription struct {
	URL       string `yaml:"url"`
	UserAgent string `yaml:"user_agent"`
}

// Operator 管道算子配置
type Operator struct {
	Type    string `yaml:"type"`
	Key     string `yaml:"key,omitempty"`
	Action  string `yaml:"action,omitempty"`
	Pattern string `yaml:"pattern,omitempty"`
	Allow   []string `yaml:"allow,omitempty"`

	// health_check 专用
	Method string          `yaml:"method,omitempty"`
	TCP    TCPCheckConfig  `yaml:"tcp,omitempty"`
	HTTP   HTTPCheckConfig `yaml:"http,omitempty"`

	// region_sample 专用
	PerRegion int    `yaml:"per_region,omitempty"`
	SortBy    string `yaml:"sort_by,omitempty"`
}

// TCPCheckConfig TCP 测速配置
type TCPCheckConfig struct {
	Concurrency int `yaml:"concurrency"`
	Timeout     int `yaml:"timeout"`
}

// HTTPCheckConfig HTTP 204 测速配置
type HTTPCheckConfig struct {
	Concurrency    int    `yaml:"concurrency"`
	Timeout        int    `yaml:"timeout"`
	URL            string `yaml:"url"`
	ExpectedStatus int    `yaml:"expected_status,omitempty"`
}

// Output 输出配置
type Output struct {
	File   string `yaml:"file"`
	Format string `yaml:"format"`
}

// CacheConfig 缓存配置
type CacheConfig struct {
	Enabled bool   `yaml:"enabled"`
	TTL     int    `yaml:"ttl"`
	Dir     string `yaml:"dir,omitempty"`
}

// Load 从文件加载配置
func Load(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	cfg.setDefaults()
	return &cfg, nil
}

func (c *Config) setDefaults() {
	if c.Output.File == "" {
		c.Output.File = "filtered_sub.txt"
	}
	if c.Output.Format == "" {
		c.Output.Format = "base64"
	}
	if c.Cache.Dir == "" {
		c.Cache.Dir = ".cache"
	}
	if c.Cache.TTL == 0 {
		c.Cache.TTL = 86400
	}
}
