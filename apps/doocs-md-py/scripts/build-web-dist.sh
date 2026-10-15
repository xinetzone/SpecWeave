#!/usr/bin/env bash
# build-web-dist.sh — 在 WSL(openKylin) + podman(node:22-alpine) 中零补丁构建 doocs/md 前端
#
# 设计要点（见 docs/build-web-dist.md，T21 补文档）：
# - 源树位于 Windows drvfs(/mnt/d)，海量小文件 I/O 极慢；rsync 到 WSL 原生 ext4 工作副本后构建。
# - pnpm store 用 podman 具名卷（原生存储），跨次构建复用。
# - npm 包走 npmmirror；node 镜像经 docker.m.daocloud.io 拉取（Docker Hub 直连被墙）。
# - 同源构建：SERVER_ENV=NETLIFY + 清空 VITE_MD_API_URL/VITE_SYNC_API_URL（Vite loadEnv
#   中进程 env 优先于 .env 文件），前端零源码补丁。
#
# 可重入：脚本可重复执行；默认保留工作副本与 node_modules 加速二次构建。
# 环境变量：MD_SRC（源树）、MD_APP_DIR（应用目录）、MD_CLEAN=1（构建后清理工作副本）。
set -euo pipefail

SRC="${MD_SRC:-/mnt/d/AI/.chaos/libs/md}"
APP_DIR="${MD_APP_DIR:-/mnt/d/AI/apps/doocs-md-py}"
WORK="$HOME/md-build/workspace"
DEST="$APP_DIR/src/doocs_md_py/assets/web-dist"
STORE_VOL="md-pnpm-store"
IMAGE="localhost/node:22-alpine"
REG="https://registry.npmmirror.com"

log() { echo "[build-web-dist] $*"; }

# ---- 0. 前置检查 ----
[ -d "$SRC/apps/web" ] || { echo "源树不存在：$SRC/apps/web" >&2; exit 1; }
command -v podman >/dev/null || { echo "未找到 podman" >&2; exit 1; }
command -v rsync >/dev/null || { echo "未找到 rsync" >&2; exit 1; }
podman image exists "$IMAGE" || {
  echo "镜像 $IMAGE 不存在，请先：podman pull docker.m.daocloud.io/library/node:22-alpine && podman tag ... $IMAGE" >&2
  exit 1
}

UPSTREAM_COMMIT="$(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo unknown)"
UPSTREAM_DIRTY="no"
git -C "$SRC" diff --quiet 2>/dev/null || UPSTREAM_DIRTY="yes"
log "上游提交：$UPSTREAM_COMMIT（工作树改动：$UPSTREAM_DIRTY）"

# ---- 1. 源树同步到原生 ext4 工作副本（保留 .git：postinstall 的 simple-git-hooks 需要）----
log "同步源树到 $WORK"
mkdir -p "$WORK"
rsync -a --delete \
  --exclude='node_modules' \
  --exclude='apps/web/dist' \
  --exclude='apps/utools/dist' \
  --exclude='apps/vscode/dist' \
  --exclude='.turbo' \
  "$SRC/" "$WORK/"

# ---- 2. 容器内安装依赖并构建 ----
log "容器构建（corepack pnpm@12.6.0 / registry=$REG）"
podman run --rm --user 0:0 \
  --network slirp4netns \
  -v "$WORK:/app:Z" \
  -v "$STORE_VOL:/pnpm/store:Z" \
  -w /app \
  -e HOME=/tmp/home \
  -e COREPACK_NPM_REGISTRY="$REG" \
  -e SERVER_ENV=NETLIFY \
  -e VITE_MD_API_URL= \
  -e VITE_SYNC_API_URL= \
  -e VITE_ACCOUNT_UI_ENABLED=true \
  -e VITE_SYNC_UI_ENABLED=true \
  -e VITE_UPLOAD_VIA_API=true \
  "$IMAGE" sh -c '
    set -eu
    mkdir -p /tmp/home /tmp/bin
    corepack enable --install-directory /tmp/bin
    export PATH=/tmp/bin:$PATH
    echo "node=$(node -v) pnpm=$(pnpm -v)"
    pnpm config set store-dir /pnpm/store
    pnpm install --frozen-lockfile --registry=https://registry.npmmirror.com
    pnpm --filter @md/web run build:h5-netlify:only
    test -f apps/web/dist/index.html
  '

# ---- 3. 产物同步到应用资产目录（保留 .gitkeep / NOTICE）----
log "同步产物到 $DEST"
mkdir -p "$DEST"
find "$DEST" -mindepth 1 \
  ! -name '.gitkeep' ! -name 'NOTICE' \
  -exec rm -rf {} + 2>/dev/null || true
cp -r "$WORK/apps/web/dist/." "$DEST/"

# ---- 4. 许可证与可复现清单 ----
cp "$SRC/LICENSE" "$DEST/LICENSE"
BUILT_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "# doocs-md-py 前端资产清单（由 scripts/build-web-dist.sh 生成）"
  echo "upstream=https://github.com/doocs/md"
  echo "upstream_commit=$UPSTREAM_COMMIT"
  echo "upstream_worktree_dirty=$UPSTREAM_DIRTY"
  echo "built_at_utc=$BUILT_AT"
  echo "image=$IMAGE (node:22-alpine)"
  echo "package_manager=pnpm@12.6.0 via corepack"
  echo "npm_registry=$REG"
  echo "build_env=SERVER_ENV=NETLIFY VITE_MD_API_URL=(empty,same-origin) VITE_SYNC_API_URL=(empty)"
  echo "build_env2=VITE_ACCOUNT_UI_ENABLED=true VITE_SYNC_UI_ENABLED=true VITE_UPLOAD_VIA_API=true"
  echo "license=WTFPL-2.0（见 LICENSE；版权归 doocs/md 上游贡献者）"
  echo "# SHA256"
  cd "$DEST"
  find . -type f ! -name 'MANIFEST.sha256' -print0 | sort -z | xargs -0 sha256sum
} > "$DEST/MANIFEST.sha256"

log "构建完成。产物："
ls -la "$DEST" | head -20
log "文件数：$(find "$DEST" -type f | wc -l)，总体积：$(du -sh "$DEST" | cut -f1)"

if [ "${MD_CLEAN:-0}" = "1" ]; then
  log "MD_CLEAN=1，清理工作副本（store 卷保留）"
  rm -rf "$WORK"
fi
