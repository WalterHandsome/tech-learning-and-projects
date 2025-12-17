#!/bin/bash

# 上传前安全检查脚本
# 使用方法: ./scripts/check-before-push.sh

echo "🔍 开始安全检查..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 检查敏感文件
echo -e "\n${YELLOW}检查敏感文件...${NC}"
SENSITIVE_FILES=(
    ".env"
    "private-notes"
    "*secret*"
    "*password*"
    "*.pem"
    "*.ppk"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    if git ls-files | grep -q "$pattern"; then
        echo -e "${RED}❌ 发现敏感文件: $pattern${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# 检查硬编码密码
echo -e "\n${YELLOW}检查硬编码密码...${NC}"
if git diff --cached | grep -i "password.*=" | grep -v "your_password" | grep -v "postgres" | grep -v "example"; then
    echo -e "${RED}❌ 发现可能的硬编码密码${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 检查 API Keys
echo -e "\n${YELLOW}检查 API Keys...${NC}"
if git diff --cached | grep -E "(ghp_|gho_|ghu_|ghs_|ghr_|sk-|AIza|AKIA)"; then
    echo -e "${RED}❌ 发现可能的 API Keys${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 检查 .gitignore
echo -e "\n${YELLOW}检查 .gitignore...${NC}"
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}❌ 缺少 .gitignore 文件${NC}"
    ERRORS=$((ERRORS + 1))
else
    if ! grep -q "private-notes" .gitignore; then
        echo -e "${YELLOW}⚠️  .gitignore 中未排除 private-notes${NC}"
    else
        echo -e "${GREEN}✅ .gitignore 配置正确${NC}"
    fi
fi

# 总结
echo -e "\n${YELLOW}检查完成${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 安全检查通过，可以安全推送${NC}"
    exit 0
else
    echo -e "${RED}❌ 发现 $ERRORS 个问题，请修复后再推送${NC}"
    exit 1
fi

