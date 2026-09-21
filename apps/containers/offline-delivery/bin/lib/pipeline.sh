# ==============================================================================
# pipeline.sh — relpack 共享片段：交付流水线共用件（单一职责=流水线机制）
#
# 四块机制，均由 bin/relpack 调用，命令实现留在 CLI 内：
#   1. wheel 版本解析与暂存（语义等价上游 _ensure_wheel_staged）
#   2. 交付骨架 CRLF shebang 守卫（pack 前置 fail-fast，见 rules §2）
#   3. release.json 清单写出（字段契约见 rules §6）
#   4. smoke 单步执行与失败指引（骨架目录取自公共变量 RELEASE_DIR）
# 依赖 log.sh（ok/warn/err/info/die）与 common.sh（win_to_wsl_path）；约定调用方先
# 设定 WHEEL_STAGE / DIST_DIR / WHEEL_GLOB / WHEEL_PREFIX / PRODUCT / WHEEL_DIST /
# RELEASE_DIR / RELEASE_NAME / APP_ROOT。
# ==============================================================================

# —— 1. wheel ——

wheel_version() {  # $1=whl 路径 → <WHEEL_PREFIX> 与 .whl 之间、-cp 之前的版本串
    local v="${1##*/}"
    v="${v#"$WHEEL_PREFIX"}"
    v="${v%.whl}"
    printf '%s' "${v%%-cp*}"
}

# 暂存区当前 whl（按 mtime 取最新；无则空）
staged_wheel() { ls -t "$WHEEL_STAGE"/$WHEEL_GLOB 2>/dev/null | head -n 1 || true; }

# 同名不等于同内容（dev0 文件名恒定，重打包只改 mtime/大小）：大小 + mtime 一致才可跳过
# 拷贝。mtime 取秒精度：Windows 侧经 drvfs/9p 暂存时纳秒位被抹平（副本恒为 .000000000），
# 用纳秒比较会每次误判为「内容已变」而反复拷贝。
wheel_fingerprint() { stat -c '%s|%Y' "$1"; }

# 清空暂存区（同时只留一个 whl，COPY glob 才确定）后拷贝并保留 mtime
_do_stage() {  # $1=源文件 $2=日志前缀
    local old
    for old in "$WHEEL_STAGE"/$WHEEL_GLOB; do
        if [ -f "$old" ]; then rm -f "$old"; fi
    done
    STAGED_WHEEL="$WHEEL_STAGE/${1##*/}"
    cp -p "$1" "$STAGED_WHEEL"
    ok "$2 → products/$PRODUCT/wheels/${1##*/}"
}

# 选择顺序：--wheel 显式 > WHEEL_DIST 最新 mtime > 复用已暂存 > 非零退出并给出上游指引
stage_wheel() {  # $1 = --wheel 值（可空）
    local explicit="${1:-}" src dist_latest
    mkdir -p "$WHEEL_STAGE"
    STAGED_WHEEL="$(staged_wheel)"
    if [ -n "$explicit" ]; then
        src="$(win_to_wsl_path "$explicit")"
        if [ ! -f "$src" ]; then die "--wheel 指定的文件不存在：$src"; fi
        case "${src##*/}" in
            "$WHEEL_PREFIX"*.whl) ;;
            *) die "--wheel 须是 $PRODUCT wheel（匹配 ${WHEEL_PREFIX}*.whl）：${src##*/}" ;;
        esac
        _do_stage "$src" "已暂存指定 wheel"
        return 0
    fi
    dist_latest="$(ls -t "$DIST_DIR"/$WHEEL_GLOB 2>/dev/null | head -n 1 || true)"
    if [ -n "$dist_latest" ]; then
        if [ -n "$STAGED_WHEEL" ] && [ "${STAGED_WHEEL##*/}" = "${dist_latest##*/}" ] \
           && [ "$(wheel_fingerprint "$STAGED_WHEEL")" = "$(wheel_fingerprint "$dist_latest")" ]; then
            ok "已是最新：wheels/${STAGED_WHEEL##*/}（同名同大小同时间，跳过拷贝）"
            return 0
        fi
        _do_stage "$dist_latest" "已暂存 $WHEEL_DIST 最新 wheel"
        return 0
    fi
    if [ -n "$STAGED_WHEEL" ]; then
        ok "复用已暂存 wheel：wheels/${STAGED_WHEEL##*/}（$WHEEL_DIST 下无 $WHEEL_GLOB）"
        return 0
    fi
    die "未找到 $PRODUCT wheel：$DIST_DIR 下无 $WHEEL_GLOB 且暂存区为空
  1) 先在上游栈产出 wheel（产物落 apps/containers/workspace/dist，注册任务 xmnn.wheel）
  2) 或用 --wheel <path> 显式指定（须匹配 ${WHEEL_PREFIX}*.whl）"
}

# —— 2. 交付骨架 CRLF shebang 守卫 ——

# 内核先按字节解析 shebang，CRLF 会让解释器名变成 bash\r，客户首跑即报
# /usr/bin/env: 'bash\r'，脚本内自救无效；artifacts/ 与 Windows 原生脚本不参与扫描。
guard_crlf_shebang() {
    local f broken=()
    while IFS= read -r f; do
        [ "$(head -c 2 "$f")" = "#!" ] || continue
        if LC_ALL=C grep -q $'\r' "$f" 2>/dev/null; then broken+=("${f#"$RELEASE_DIR"/}"); fi
    done < <(find "$RELEASE_DIR" -type f ! -path "$RELEASE_DIR/artifacts/*" \
                 ! -name '*.ps1' ! -name '*.psm1' ! -name '*.bat' ! -name '*.cmd')
    if [ "${#broken[@]}" -eq 0 ]; then return 0; fi
    err "交付骨架存在 CRLF shebang 脚本：${broken[*]}；客户首跑会报 /usr/bin/env: 'bash\r'——请在仓库根执行 git add --renormalize . 修复行尾后重新打包"
    return 1
}

# —— 3. release.json 清单 ——

# $1=artifacts 目录 $2=交付版本 $3=暂存 whl 路径 $4=wheel 版本 $5=镜像 id
# $6=torch JSON 值（"版本" 或 null）$7=归档文件名 $8=归档字节数 $9=归档 sha256
write_release_manifest() {
    local artifacts="$1" ver="$2" staged="$3" wheel_ver="$4" image_id="$5" torch_json="$6" \
          archive="$7" size="$8" sha="$9" built_at commit
    built_at="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"   # UTC ISO8601 秒精度
    commit="$(git -C "$APP_ROOT" rev-parse HEAD 2>/dev/null || true)"
    if [ -z "$commit" ]; then commit="unknown"; fi
    cat > "$artifacts/release.json" <<EOF
{
  "schema_version": "1",
  "product": "$PRODUCT",
  "version": "$ver",
  "wheel": {
    "file": "${staged##*/}",
    "version": "$wheel_ver",
    "size_bytes": $(stat -c '%s' "$staged")
  },
  "image": {
    "ref": "$PRODUCT:$ver",
    "id": "$image_id",
    "torch_cpu": $torch_json,
    "abi": "cp314-gil"
  },
  "archive": {
    "file": "$archive",
    "size_bytes": $size,
    "sha256": "$sha"
  },
  "built_at": "$built_at",
  "source_commit": "$commit",
  "pack_tool": "offline-delivery.relpack"
}
EOF
}

# —— 4. smoke 单步执行与失败指引 ——

# 在交付骨架目录内执行一步（$1=步骤名，其余=骨架内命令）。骨架目录只从公共变量
# RELEASE_DIR 读取，**不得**混进命令参数：否则 shift 后 "$@" 的首项变成目录本身，
# 子 shell 会去执行该目录而报 `Is a directory`（exit 126）。
run_smoke_step() {  # $1=步骤名，其余=骨架内命令
    local label="$1"; shift
    info "【$label】$*"
    (cd "$RELEASE_DIR" && "$@")
}

smoke_hint() {  # $1=失败步骤 $2=退出码
    err "smoke 步骤 $1 失败（exit $2，原始输出见上）；常见原因与处置：
  · 端口被占用 → 改 $RELEASE_NAME/.env 的 XMNN_SSH_PORT / XMNN_JUPYTER_PORT，或先 ./xmnnctl down
  · 缺 podman-compose → 在 WSL 内 pipx install podman-compose（并确认 ~/.local/bin 在 PATH）
  · Podman 后台未启动 → podman machine start；镜像未导入 → 先 ./xmnnctl load"
}