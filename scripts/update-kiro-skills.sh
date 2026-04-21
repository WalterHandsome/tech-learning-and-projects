#!/bin/bash
# Kiro Skills 更新脚本
# 用法: ./scripts/update-kiro-skills.sh
# 说明: 从 GitHub 拉取最新版本的第三方 Skills，覆盖本地安装

set -e

# ============================================================
# 配置区：在这里管理所有第三方 Skill 的来源
# ============================================================

REPO_URL="https://github.com/addyosmani/agent-skills.git"
REPO_NAME="agent-skills"
TMP_DIR="/tmp/kiro-skill-update-${REPO_NAME}"

# 全局 Skills（所有项目生效）
GLOBAL_SKILLS=(
  "planning-and-task-breakdown"
  "incremental-implementation"
  "debugging-and-error-recovery"
  "code-simplification"
)

# Brand Agent 专属 Skills
BRAND_AGENT_DIR="$HOME/PycharmProjects/personal-brand-agent"
BRAND_AGENT_SKILLS=(
  "spec-driven-development"
  "api-and-interface-design"
)

# ============================================================
# 执行更新
# ============================================================

echo "🔄 开始更新 Kiro Skills..."
echo "   来源: $REPO_URL"
echo ""

# 清理旧的临时目录
rm -rf "$TMP_DIR"

# 克隆最新版本
echo "📥 拉取最新版本..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR" 2>/dev/null
echo ""

# 获取最新 commit 信息
LATEST_COMMIT=$(cd "$TMP_DIR" && git log -1 --format="%h %s (%ci)")
echo "📌 最新版本: $LATEST_COMMIT"
echo ""

# 更新全局 Skills
echo "🌐 更新全局 Skills..."
for skill in "${GLOBAL_SKILLS[@]}"; do
  if [ -f "$TMP_DIR/skills/$skill/SKILL.md" ]; then
    mkdir -p "$HOME/.kiro/skills/$skill"
    cp "$TMP_DIR/skills/$skill/SKILL.md" "$HOME/.kiro/skills/$skill/SKILL.md"
    echo "   ✅ $skill"
  else
    echo "   ⚠️  $skill — 上游已删除或重命名，请检查"
  fi
done
echo ""

# 更新 Brand Agent Skills
echo "🤖 更新 Brand Agent Skills..."
for skill in "${BRAND_AGENT_SKILLS[@]}"; do
  if [ -f "$TMP_DIR/skills/$skill/SKILL.md" ]; then
    mkdir -p "$BRAND_AGENT_DIR/.kiro/skills/$skill"
    cp "$TMP_DIR/skills/$skill/SKILL.md" "$BRAND_AGENT_DIR/.kiro/skills/$skill/SKILL.md"
    echo "   ✅ $skill"
  else
    echo "   ⚠️  $skill — 上游已删除或重命名，请检查"
  fi
done
echo ""

# 检查上游是否有新增 Skills
echo "📋 上游所有可用 Skills:"
for dir in "$TMP_DIR/skills"/*/; do
  skill_name=$(basename "$dir")
  installed=""
  for s in "${GLOBAL_SKILLS[@]}" "${BRAND_AGENT_SKILLS[@]}"; do
    if [ "$s" = "$skill_name" ]; then
      installed=" ← 已安装"
      break
    fi
  done
  echo "   - $skill_name$installed"
done
echo ""

# 清理
rm -rf "$TMP_DIR"

# 记录更新时间
UPDATE_LOG="$HOME/.kiro/skills/.update-log"
echo "[$(date '+%Y-%m-%d %H:%M')] 更新自 $REPO_URL ($LATEST_COMMIT)" >> "$UPDATE_LOG"

echo "✅ 更新完成！"
echo "📝 更新日志: $UPDATE_LOG"
echo ""
echo "💡 提示: 如果上游有新增的 Skill 你想安装，编辑本脚本的 GLOBAL_SKILLS 或 BRAND_AGENT_SKILLS 数组即可。"
