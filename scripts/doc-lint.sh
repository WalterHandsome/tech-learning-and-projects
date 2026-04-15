#!/bin/bash

# 文档质量检查脚本（兼容 macOS 和 Linux）
# 使用方法: ./scripts/doc-lint.sh [目录路径]
# 示例: ./scripts/doc-lint.sh learning-notes/ai-agent

DOC_DIR="${1:-learning-notes}"

echo "📝 开始文档质量检查: $DOC_DIR"
echo "================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# ============================================
# 1. Markdown 格式检查
# ============================================
echo -e "\n${CYAN}[1/6] Markdown 格式检查${NC}"

# 检查未标注语言的代码块
find "$DOC_DIR" -name "*.md" -type f | while read -r file; do
    matches=$(grep -n '^```$' "$file" 2>/dev/null)
    if [ -n "$matches" ]; then
        echo "$matches" | while IFS= read -r match; do
            line_num=$(echo "$match" | cut -d: -f1)
            echo -e "${YELLOW}⚠️  未标注语言的代码块: $file:$line_num${NC}"
        done
    fi
done

# 检查标题层级跳跃（如 # 直接到 ###，跳过代码块内的内容）
find "$DOC_DIR" -name "*.md" -type f | while read -r file; do
    prev_level=0
    line_num=0
    in_code_block=0
    while IFS= read -r line; do
        line_num=$((line_num + 1))
        # 跟踪代码块状态
        if echo "$line" | grep -qE '^\`\`\`'; then
            if [ $in_code_block -eq 0 ]; then
                in_code_block=1
            else
                in_code_block=0
            fi
            continue
        fi
        # 跳过代码块内的内容
        if [ $in_code_block -eq 1 ]; then
            continue
        fi
        if echo "$line" | grep -qE '^#{1,6} .+'; then
            level=$(echo "$line" | sed 's/^\(#*\).*/\1/' | wc -c)
            level=$((level - 1))
            if [ $prev_level -gt 0 ] && [ $((level - prev_level)) -gt 1 ]; then
                echo -e "${YELLOW}⚠️  标题层级跳跃 (h$prev_level → h$level): $file:$line_num${NC}"
            fi
            prev_level=$level
        fi
    done < "$file"
done

echo -e "${GREEN}✅ Markdown 格式检查完成${NC}"

# ============================================
# 2. 内部链接检查
# ============================================
echo -e "\n${CYAN}[2/6] 内部链接检查${NC}"

find "$DOC_DIR" -name "*.md" -type f | while read -r file; do
    dir=$(dirname "$file")

    # 提取 Markdown 链接中的 .md 引用: [text](path.md)
    grep -oE '\[.*\]\([^)]+\.md\)' "$file" 2>/dev/null | sed 's/.*(\(.*\.md\))/\1/' | while read -r link; do
        # 跳过 http 链接
        case "$link" in
            http*) continue ;;
        esac
        # 解码 %20 为空格
        decoded_link=$(echo "$link" | sed 's/%20/ /g')
        # 解析相对路径
        target="$dir/$decoded_link"
        if [ ! -f "$target" ]; then
            echo -e "${RED}❌ 断裂链接: $file → $link${NC}"
        fi
    done

    # 检查 "详见 → xxx.md" 格式的引用
    grep -oE '详见[[:space:]]*→[[:space:]]*[^[:space:]]+\.md' "$file" 2>/dev/null | sed 's/详见[[:space:]]*→[[:space:]]*//' | while read -r ref; do
        found=0
        if [ -f "$dir/$ref" ]; then
            found=1
        fi
        if [ $found -eq 0 ]; then
            result=$(find "$DOC_DIR" -name "$(basename "$ref")" -type f 2>/dev/null | head -1)
            if [ -n "$result" ]; then
                found=1
            fi
        fi
        if [ $found -eq 0 ]; then
            echo -e "${RED}❌ 引用文件不存在: $file → $ref${NC}"
        fi
    done
done

echo -e "${GREEN}✅ 内部链接检查完成${NC}"

# ============================================
# 3. 文件头部规范检查
# ============================================
echo -e "\n${CYAN}[3/6] 文件头部规范检查${NC}"

MISSING_TITLE=0
find "$DOC_DIR" -name "*.md" -type f ! -name "README.md" ! -name ".audit-progress.md" | while read -r file; do
    first_content_line=$(grep -m1 -v '^\s*$' "$file" | head -1)
    if ! echo "$first_content_line" | grep -qE '^# '; then
        echo -e "${YELLOW}⚠️  缺少一级标题: $file${NC}"
    fi
done

echo -e "${GREEN}✅ 文件头部检查完成${NC}"

# ============================================
# 4. 版本时效性检查
# ============================================
echo -e "\n${CYAN}[4/6] 版本时效性标记检查${NC}"

VERSIONED=$(grep -rl "version-check:" "$DOC_DIR" --include="*.md" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=$(find "$DOC_DIR" -name "*.md" -type f ! -name "README.md" ! -name ".audit-progress.md" | wc -l | tr -d ' ')

echo -e "  版本标记覆盖率: ${VERSIONED}/${TOTAL} 个文件"

if [ "$VERSIONED" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  尚无文件添加版本标记，建议逐步添加 <!-- version-check: ... --> 注释${NC}"
fi

# 检查超过 90 天未检查的版本标记
NINETY_DAYS_AGO=$(date -v-90d +%Y-%m-%d 2>/dev/null || date -d "90 days ago" +%Y-%m-%d 2>/dev/null)
if [ -n "$NINETY_DAYS_AGO" ]; then
    grep -rn "version-check:.*checked" "$DOC_DIR" --include="*.md" 2>/dev/null | while IFS= read -r match; do
        check_date=$(echo "$match" | grep -oE 'checked [0-9]{4}-[0-9]{2}-[0-9]{2}' | sed 's/checked //')
        if [ -n "$check_date" ] && [[ "$check_date" < "$NINETY_DAYS_AGO" ]]; then
            file=$(echo "$match" | cut -d: -f1)
            echo -e "${YELLOW}⚠️  版本标记过期 (${check_date}): $file${NC}"
        fi
    done
fi

echo -e "${GREEN}✅ 版本时效性检查完成${NC}"

# ============================================
# 5. 内容质量快速检查
# ============================================
echo -e "\n${CYAN}[5/6] 内容质量快速检查${NC}"

# 检查空文件或过短文件（少于 10 行）
find "$DOC_DIR" -name "*.md" -type f ! -name "README.md" | while read -r file; do
    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -lt 10 ]; then
        echo -e "${YELLOW}⚠️  内容过少 (${lines} 行): $file${NC}"
    fi
done

# 检查重复标题（同级别）
find "$DOC_DIR" -name "*.md" -type f | while read -r file; do
    dup=$(grep -E '^#{1,3} ' "$file" | sort | uniq -d)
    if [ -n "$dup" ]; then
        echo -e "${YELLOW}⚠️  重复标题: $file${NC}"
        echo "$dup" | head -3 | while IFS= read -r d; do
            echo -e "     → $d"
        done
    fi
done

echo -e "${GREEN}✅ 内容质量检查完成${NC}"

# ============================================
# 6. 目录结构一致性检查
# ============================================
echo -e "\n${CYAN}[6/6] 目录结构一致性检查${NC}"

# 检查 README.md 中提到的目录是否都存在
if [ -f "$DOC_DIR/ai-agent/README.md" ]; then
    # 检查实际存在但 README 未提及的目录
    for dir in "$DOC_DIR"/ai-agent/*/; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            if ! grep -q "$dirname" "$DOC_DIR/ai-agent/README.md" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  目录存在但 README 未提及: $dirname${NC}"
            fi
        fi
    done
fi

echo -e "${GREEN}✅ 目录结构检查完成${NC}"

# ============================================
# 总结
# ============================================
echo -e "\n================================================"
TOTAL_FILES=$(find "$DOC_DIR" -name "*.md" -type f | wc -l | tr -d ' ')
echo -e "📊 检查完成: 共扫描 ${TOTAL_FILES} 个 Markdown 文件"
echo -e "💡 提示: 使用 ${CYAN}./scripts/doc-lint.sh learning-notes/ai-agent${NC} 检查特定目录"
