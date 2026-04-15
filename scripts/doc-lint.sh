#!/bin/bash

# 文档质量检查脚本（兼容 macOS 和 Linux）
# 使用方法: ./scripts/doc-lint.sh [目录路径]
# 示例: ./scripts/doc-lint.sh learning-notes/ai-agent
#
# 设计原则：
# - 只检查能确定对错的问题（断裂链接、缺少标题、文件过短）
# - 不检查代码块语言标注（ASCII 图表/流程图不需要语言标记）
# - 不检查标题层级跳跃（shell 无法可靠区分代码块内外的 # 符号）

DOC_DIR="${1:-learning-notes}"

echo "📝 开始文档质量检查: $DOC_DIR"
echo "================================================"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================
# 1. 内部链接检查
# ============================================
echo -e "\n${CYAN}[1/5] 内部链接检查${NC}"

find "$DOC_DIR" -name "*.md" -type f | sort | while read -r file; do
    dir=$(dirname "$file")

    # 逐行检查 Markdown 链接，避免贪婪匹配问题
    grep -n '](.*\.md)' "$file" 2>/dev/null | while IFS= read -r match_line; do
        line_num=$(echo "$match_line" | cut -d: -f1)
        line_content=$(echo "$match_line" | cut -d: -f2-)

        # 提取所有 (xxx.md) 中的路径，非贪婪方式
        echo "$line_content" | grep -oE '\([^)]+\.md\)' | sed 's/^(//;s/)$//' | while read -r link; do
            case "$link" in
                http*) continue ;;
            esac
            decoded_link=$(echo "$link" | sed 's/%20/ /g')
            target="$dir/$decoded_link"
            if [ ! -f "$target" ]; then
                echo -e "${RED}❌ 断裂链接: $file:$line_num → $link${NC}"
            fi
        done
    done

    # 检查纯文本引用（未使用 Markdown 链接格式的 "详见 → xxx.md"）
    grep -n '详见.*→.*\.md' "$file" 2>/dev/null | while IFS= read -r match_line; do
        line_num=$(echo "$match_line" | cut -d: -f1)
        line_content=$(echo "$match_line" | cut -d: -f2-)
        # 如果这行已经包含 [text](link) 格式，跳过
        if echo "$line_content" | grep -q '\[.*\](.*\.md)'; then
            continue
        fi
        echo -e "${YELLOW}⚠️  纯文本引用建议改为 Markdown 链接: $file:$line_num${NC}"
    done
done

echo -e "${GREEN}✅ 内部链接检查完成${NC}"

# ============================================
# 2. 文件头部规范检查
# ============================================
echo -e "\n${CYAN}[2/5] 文件头部规范检查${NC}"

find "$DOC_DIR" -name "*.md" -type f \
    ! -name "README.md" \
    ! -name ".audit-progress.md" \
    ! -name ".update-log.md" \
    ! -name ".DS_Store" \
    | sort | while read -r file; do
    basename_file=$(basename "$file")
    case "$basename_file" in
        .*) continue ;;
    esac
    first_content_line=$(grep -m1 -v '^\s*$' "$file" 2>/dev/null)
    if ! echo "$first_content_line" | grep -qE '^# '; then
        echo -e "${YELLOW}⚠️  缺少一级标题: $file${NC}"
    fi
done

echo -e "${GREEN}✅ 文件头部检查完成${NC}"

# ============================================
# 3. 版本时效性检查
# ============================================
echo -e "\n${CYAN}[3/5] 版本时效性标记检查${NC}"

VERSIONED=$(grep -rl "version-check:" "$DOC_DIR" --include="*.md" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=$(find "$DOC_DIR" -name "*.md" -type f \
    ! -name "README.md" \
    ! -name ".audit-progress.md" \
    ! -name ".update-log.md" \
    ! -name ".DS_Store" \
    | wc -l | tr -d ' ')

echo -e "  版本标记覆盖率: ${VERSIONED}/${TOTAL} 个文件"

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
# 4. 内容质量快速检查
# ============================================
echo -e "\n${CYAN}[4/5] 内容质量快速检查${NC}"

find "$DOC_DIR" -name "*.md" -type f ! -name "README.md" ! -name ".DS_Store" | sort | while read -r file; do
    basename_file=$(basename "$file")
    case "$basename_file" in
        .*) continue ;;
    esac
    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -lt 10 ]; then
        echo -e "${YELLOW}⚠️  内容过少 (${lines} 行): $file${NC}"
    fi
done

echo -e "${GREEN}✅ 内容质量检查完成${NC}"

# ============================================
# 5. 目录结构一致性检查
# ============================================
echo -e "\n${CYAN}[5/5] 目录结构一致性检查${NC}"

if [ -f "$DOC_DIR/ai-agent/README.md" ]; then
    for dir in "$DOC_DIR"/ai-agent/*/; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            case "$dirname" in
                .*|image) continue ;;
            esac
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
