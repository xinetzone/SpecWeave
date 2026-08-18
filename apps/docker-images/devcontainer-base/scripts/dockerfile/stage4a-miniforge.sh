#!/bin/bash
# =============================================================================
# Stage 4a/4c: Miniforge3 (conda-forge) 安装 + .condarc 配置
# 变化频率：低（Miniforge安装器版本、镜像配置很少改动）
# 缓存保护：此层独立，后续4b(mamba create)和4c(pip+验证)的修改不触发本层重跑
# =============================================================================
set -e

echo "=== Stage 4a/4c: Install Miniforge3 + configure .condarc ==="
_STAGE_START=$(date +%s)

# ── 架构检测 + Miniforge3安装器URL ──
echo "[INFO] Detecting architecture..."
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)  CONDA_ARCH="x86_64" ;;
    aarch64) CONDA_ARCH="aarch64" ;;
    *) echo "[ERROR] Unsupported architecture: $ARCH"; exit 1 ;;
esac
echo "[OK] Architecture: $ARCH ($CONDA_ARCH)"

# ── 下载并安装 Miniforge3（conda-forge官方发行版，无defaults包，原生libmamba支持） ──
echo "[INFO] Downloading Miniforge3 installer (conda-forge official)..."
_dl_start=$(date +%s)

LOCAL_INSTALLER=""
for f in /tmp/local-cache/Miniforge3-Latest-Linux-${CONDA_ARCH}.sh \
         /tmp/local-cache/Miniforge3-*-Linux-${CONDA_ARCH}.sh; do
    if [ -f "$f" ] && [ -s "$f" ]; then
        LOCAL_INSTALLER="$f"
        break
    fi
done

if [ -n "$LOCAL_INSTALLER" ]; then
    echo "[OK] Using local cached installer: $LOCAL_INSTALLER ($(du -h "$LOCAL_INSTALLER" | cut -f1))"
    cp "$LOCAL_INSTALLER" /tmp/miniforge.sh
    DL_OK=1
else
    echo "[INFO] No local cache found, downloading from network..."
    # Miniforge3下载源：GitHub官方 + 国内镜像
    if [ "${CONDA_MIRROR}" = "tuna" ]; then
        DL_URLS=(
            "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-${CONDA_ARCH}.sh"
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    elif [ "${CONDA_MIRROR}" = "aliyun" ]; then
        DL_URLS=(
            "https://mirrors.aliyun.com/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-${CONDA_ARCH}.sh"
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    else
        DL_URLS=(
            "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-${CONDA_ARCH}.sh"
        )
    fi

    DL_OK=0
    for dl_url in "${DL_URLS[@]}"; do
        echo "[INFO] Trying: $dl_url"
        if curl -fsSL --connect-timeout 30 --max-time 300 --retry 3 --retry-delay 5 \
            -L -o /tmp/miniforge.sh "$dl_url" 2>/tmp/conda_dl_err.log; then
            echo "[OK] Downloaded from: $dl_url"
            DL_OK=1
            break
        else
            echo "[WARN] Failed, trying next source..."
            cat /tmp/conda_dl_err.log | tail -3
        fi
    done

    if [ "$DL_OK" = "0" ]; then
        echo "[ERROR] Failed to download Miniforge3 from all sources"
        cat /tmp/conda_dl_err.log
        exit 1
    fi
fi

_dl_elapsed=$(($(date +%s) - _dl_start))
echo "[OK] Installer ready: $(du -h /tmp/miniforge.sh | cut -f1) in ${_dl_elapsed}s"

echo "[INFO] Installing Miniforge3 to ${CONDA_DIR}..."
bash /tmp/miniforge.sh -b -p "${CONDA_DIR}" -f
rm -f /tmp/miniforge.sh
echo "[OK] Miniforge3 installed: $("${CONDA_DIR}/bin/conda" --version 2>&1)"

# ── Source conda.sh 使 conda 命令在当前 shell 完全可用 ──
. "${CONDA_DIR}/etc/profile.d/conda.sh"
echo "[OK] conda.sh sourced, conda available in build shell"

# ── Miniforge3默认已配置conda-forge channel和libmamba solver，无需额外ToS/defaults清理 ──
echo "[INFO] Miniforge3 defaults: conda-forge channel + libmamba solver pre-configured"

# ── 写入系统级 .condarc（镜像源 + libmamba solver + 性能参数） ──
echo "[ACTION] Writing system-level ${CONDA_DIR}/.condarc with mirror sources..."
case "${CONDA_MIRROR}" in
    bfsu)
        echo "[INFO] Configuring conda for BFSU mirror (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 120' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
    tuna)
        echo "[INFO] Configuring conda for Tsinghua TUNA mirror (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 120' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
    *)
        echo "[INFO] Configuring conda for official channels (conda-forge only, no defaults)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > "${CONDA_DIR}/.condarc"
        ;;
esac
echo "[OK] System-level .condarc written:"
cat "${CONDA_DIR}/.condarc"
echo "[INFO] mamba version: $(mamba --version 2>&1 | head -1)"

# ── Miniforge3自带Python，不要升级base Python（conda无cp314t构建） ──
_builtin_py=$("${CONDA_DIR}/bin/python" --version 2>&1 | awk '{print $2}')
echo "[INFO] Miniforge3 base Python (conda runtime): ${_builtin_py}"
echo "[INFO] Note: conda base Python kept as-is; free-threading Python will be in 'main' env"

# ── 清理临时文件 ──
rm -f /tmp/conda_dl_err.log 2>/dev/null || true

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "[TIMER] Stage 4a/4c (miniforge+.condarc) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"
echo '[OK] Stage 4a complete'
