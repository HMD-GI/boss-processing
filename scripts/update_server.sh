#!/usr/bin/env bash
# ============================================================
# 服务器端自动构建 & 推送脚本（在国内服务器运行，构建推送都很快）
#
# 手动执行一次：
#   bash scripts/update_server.sh
#
# 全自动（crontab 每 2 分钟轮询一次，有.gitignore 变化才构建）：
#   */2 * * * * cd /opt/boss && bash scripts/update_server.sh >> /opt/boss/backups/update.log 2>&1
#
# 工作流程：git pull → 检测到新提交 → 构建 backend/frontend
#           → docker push 到 ACR → Watchtower 感知新镜像并滚动更新容器
#
# 前置条件（一次性，已在部署步骤中完成）：
#   1) 服务器已安装 docker 与 git
#   2) 已完成 docker login（凭据保存在 ~/.docker/config.json）
#   3) /opt/boss 目录是 git clone 的仓库
#
# 可选环境变量（不设置则用默认值，按你实际 ACR 地域/命名空间修改）：
#   ACR_REGISTRY  (默认 registry.cn-hangzhou.aliyuncs.com)
#   ACR_NAMESPACE (默认 boss-processing)
#   ACR_USERNAME  (可留空，凭据已在 config.json)
# ============================================================
set -euo pipefail

REPO_DIR="${1:-/opt/boss}"
REGISTRY="${ACR_REGISTRY:-registry.cn-hangzhou.aliyuncs.com}"
NAMESPACE="${ACR_NAMESPACE:-boss-processing}"
STAMP="$(date '+%F %T')"
LOG="${REPO_DIR}/backups/update.log"

mkdir -p "$(dirname "$LOG")"
cd "$REPO_DIR"

# ① 拉取最新代码
git fetch origin || { echo "[$STAMP] git fetch 失败"; exit 1; }
if git diff --quiet FETCH_HEAD HEAD; then
  echo "[$STAMP] 无新提交，跳过构建。"
  exit 0
fi

echo "[$STAMP] 检测到新提交，开始构建..."
git reset --hard FETCH_HEAD

# ② 构建并推送 backend（docker login 凭据已保存在服务器 config.json）
echo "[$STAMP] 构建 backend..."
docker build -f Dockerfile.backend -t "${REGISTRY}/${NAMESPACE}/backend:latest" .
echo "[$STAMP] 推送 backend..."
docker push "${REGISTRY}/${NAMESPACE}/backend:latest"

# ③ 构建并推送 frontend
echo "[$STAMP] 构建 frontend..."
docker build -f frontend/Dockerfile -t "${REGISTRY}/${NAMESPACE}/frontend:latest" .
echo "[$STAMP] 推送 frontend..."
docker push "${REGISTRY}/${NAMESPACE}/frontend:latest"

echo "[$STAMP] 全部完成。Watchtower 将在几分钟内自动拉取新镜像并更新容器。"
echo "[$STAMP] 如需立即生效：docker compose pull && docker compose up -d backend frontend"