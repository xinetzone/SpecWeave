# ==============================================================================
# pipeline.sh — relpack 共享片段：交付流水线共用件（单一职责=流水线机制）
#
# 五块机制，均由 bin/relpack 调用，命令实现留在 CLI 内：
#   1. 载荷 wheel 版本解析与暂存（暂存区 = 交付包内 release/payload/）
#   2. 载荷依赖集（deps.txt）提取 / 一致性校验 / 重写（零 Python：unzip|bsdtar）
#   3. 交付骨架 CRLF shebang 守卫（pack 前置 fail-fast，见 rules §2）
#   4. release.json（schema v2：载荷在前、底座镜像、底座归档）清单写出
#   5. smoke 单步执行与失败指引（骨架目录取自公共变量 RELEASE_DIR）
# 依赖 log.sh（ok/warn/err/info/die）与 common.sh（win_to_wsl_path）；约定调用方先
# 设定 WHEEL_STAGE / DIST_DIR / WHEEL_GLOB / WHEEL_PREFIX / PRODUCT / WHEEL_DIST /
# RELEASE_DIR / RELEASE_NAME / DEPS_FILE / APP_ROOT。
# ==============================================================================

# —— 1. 载荷 wheel ——

wheel_version() {  # $1=whl 路径 → <WHEEL_PREFIX> 与 .whl 之间、-cp 之前的版本串
    local v="${1##*/}"
    v="${v#"$WHEEL_PREFIX"}"
    v="${v%.whl}"
    printf '%s' "${v%%-cp*}"
}

# 载荷区当前 whl（按 mtime 取最新；无则空）
staged_wheel() { ls -t "$WHEEL_STAGE"/$WHEEL_GLOB 2>/dev/null | head -n 1 || true; }

# 载荷区 whl 个数（交付包只能随带一个，pack/smoke 前置守卫用）
staged_wheel_count() { ls "$WHEEL_STAGE"/$WHEEL_GLOB 2>/dev/null | wc -l | tr -d ' '; }

# 恰有一个载荷 whl 时打印其路径；否则非零退出并给出上游指引
require_staged_wheel() {
    local count
    count="$(staged_wheel_count)"
    if [ "$count" = 0 ]; then
        die "未找到载荷 wheel：products/$PRODUCT/$RELEASE_NAME/payload/ 下无 $WHEEL_GLOB
  1) 先在上游栈产出 wheel（产物落 apps/containers/workspace/dist，注册任务 xmnn.wheel）
  2) 再执行 bin/relpack stage（或用 --wheel <path> 显式指定，须匹配 ${WHEEL_PREFIX}*.whl）"
    fi
    if [ "$count" != 1 ]; then
        die "载荷区有 $count 个 wheel（须恰一个）：products/$PRODUCT/$RELEASE_NAME/payload/
  交付包只能随带一个载荷；请清理多余 whl 后重试（stage 只留最新一个）"
    fi
    staged_wheel
}

# 同名不等于同内容（dev0 文件名恒定，重打包只改 mtime/大小）：大小 + mtime 一致才可跳过
# 拷贝。mtime 取秒精度：Windows 侧经 drvfs/9p 暂存时纳秒位被抹平（副本恒为 .000000000），
# 用纳秒比较会每次误判为「内容已变」而反复拷贝。
wheel_fingerprint() { stat -c '%s|%Y' "$1"; }

# 清空载荷区（同时只留一个 whl，交付包内载荷才确定）后拷贝并保留 mtime
_do_stage() {  # $1=源文件 $2=日志前缀
    local old
    for old in "$WHEEL_STAGE"/$WHEEL_GLOB; do
        if [ -f "$old" ]; then rm -f "$old"; fi
    done
    STAGED_WHEEL="$WHEEL_STAGE/${1##*/}"
    cp -p "$1" "$STAGED_WHEEL"
    ok "$2 → products/$PRODUCT/$RELEASE_NAME/payload/${1##*/}"
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
            ok "已是最新：payload/${STAGED_WHEEL##*/}（同名同大小同时间，跳过拷贝）"
            return 0
        fi
        _do_stage "$dist_latest" "已暂存 $WHEEL_DIST 最新 wheel"
        return 0
    fi
    if [ -n "$STAGED_WHEEL" ]; then
        ok "复用已暂存 wheel：payload/${STAGED_WHEEL##*/}（$WHEEL_DIST 下无 $WHEEL_GLOB）"
        return 0
    fi
    die "未找到 $PRODUCT wheel：$DIST_DIR 下无 $WHEEL_GLOB 且载荷区为空
  1) 先在上游栈产出 wheel（产物落 apps/containers/workspace/dist，注册任务 xmnn.wheel）
  2) 或用 --wheel <path> 显式指定（须匹配 ${WHEEL_PREFIX}*.whl）"
}

# sha256 十六进制（优先 GNU sha256sum，回退 Perl shasum，macOS/BSD 可用）；两者皆缺返回 1
sha256_of() {
    local out=""
    if command -v sha256sum >/dev/null 2>&1; then out="$(sha256sum "$1" | cut -d' ' -f1)"
    elif command -v shasum >/dev/null 2>&1; then out="$(shasum -a 256 "$1" | cut -d' ' -f1)"
    else return 1; fi
    printf '%s' "$out" | tr 'A-Z' 'a-z'
}

# —— 2. 载荷依赖集（deps.txt）——

# 从 whl 读出 *.dist-info/METADATA（unzip -p 优先，回退 bsdtar -xOf）；
# 两者皆不可用（或皆读不出）→ 返回 2：调用方必须 [WARN] 告警后跳过，不得静默通过
# （没校验就宣称一致）、也不得硬失败（缺工具不该阻断交付流水线）。
wheel_metadata() {  # $1=whl 路径
    local whl="$1"
    if command -v unzip >/dev/null 2>&1; then
        unzip -p "$whl" '*.dist-info/METADATA' 2>/dev/null && return 0
    fi
    if command -v bsdtar >/dev/null 2>&1; then
        bsdtar -xOf "$whl" '*.dist-info/METADATA' 2>/dev/null && return 0
    fi
    return 2
}

# 无条件运行时依赖（Requires-Dist 中**不含分号**者：去前缀、去尾空白、排序去重）→ $2
collect_wheel_deps() {  # $1=whl 路径 $2=输出文件；返回 2=无解压工具
    local whl="$1" out="$2" meta
    meta="$(wheel_metadata "$whl")" || return 2
    printf '%s\n' "$meta" | awk '
        BEGIN { in_headers = 1 }
        in_headers && /^[[:space:]]*$/ { in_headers = 0; next }
        in_headers && /^Requires-Dist:/ {
            line = $0
            sub(/^Requires-Dist:[[:space:]]*/, "", line)
            sub(/\r$/, "", line)
            if (index(line, ";") == 0 && length(line) > 0) print line
        }' | LC_ALL=C sort -u > "$out"
    return 0
}

# deps.txt 内的依赖行（去注释/去空行/去尾空白，排序去重）→ $2；文件缺失返回 1
collect_deps_file() {  # $1=deps 文件 $2=输出文件
    [ -f "$1" ] || return 1
    { grep -v '^[[:space:]]*#' "$1" || true; } \
        | sed 's/\r$//; s/[[:space:]]*$//' \
        | { grep -v '^[[:space:]]*$' || true; } \
        | LC_ALL=C sort -u > "$2"
}

# 载荷依赖集与 deps.txt 的一致性校验（deps 命令与 pack 前置守卫共用）：
#   0 = 一致；1 = 不一致或 deps.txt 缺失（已打印差异清单 + 中文指引）；2 = 无法校验（已告警）
deps_consistency() {  # $1=载荷 whl $2=deps 文件
    local whl="$1" file="$2" dir act exp
    dir="$(mktemp -d "${TMPDIR:-/tmp}/relpack-deps.XXXXXX" 2>/dev/null)" || dir=""
    if [ -z "$dir" ]; then
        warn "无法创建临时目录：跳过 deps 一致性校验（未校验即通过，请检查 TMPDIR）"
        return 2
    fi
    act="$dir/actual.txt"; exp="$dir/expected.txt"
    if ! collect_wheel_deps "$whl" "$act"; then
        warn "未找到 unzip 或 bsdtar：无法从 ${whl##*/} 读出依赖集，本次跳过 deps 校验（不是通过，也未阻断）
  处置：安装 unzip（Info-ZIP）或 bsdtar（libarchive-tar）后重试（WSL / 常规 Linux 自带 unzip）"
        rm -rf "$dir"; return 2
    fi
    if command -v diff >/dev/null 2>&1; then :; else
        warn "未找到 diff：跳过 deps 一致性校验（不是通过，也未阻断）"
        rm -rf "$dir"; return 2
    fi
    if [ ! -f "$file" ]; then
        err "缺少依赖集文件：products/$PRODUCT/deps.txt（底座依赖面的唯一事实源）"
        err "  生成：bin/relpack deps --write"
        err "  依赖集变化必须重发底座镜像：bin/relpack build 后重新 pack"
        rm -rf "$dir"; return 1
    fi
    collect_deps_file "$file" "$exp"
    if diff "$exp" "$act" > "$dir/diff.txt" 2>&1; then
        ok "依赖集一致：products/$PRODUCT/deps.txt（$(wc -l < "$act" | tr -d ' ') 项无条件依赖）"
        rm -rf "$dir"; return 0
    fi
    err "载荷依赖集与 products/$PRODUCT/deps.txt 不一致（差异清单：< 仅 deps.txt；> 仅载荷 whl）："
    sed 's/^/    /' "$dir/diff.txt" >&2
    err "依赖集变化必须重发底座镜像：bin/relpack build 后重新 pack"
    err "对齐方式：bin/relpack deps --write（随后必须重建底座镜像）"
    rm -rf "$dir"; return 1
}

# 无既有头部时的默认头部注释块（三行值由参数注入）
_deps_default_header() {  # $1=whl 名 $2=sha256 $3=生成时间
    printf '%s\n' \
        '# =============================================================================' \
        "# $PRODUCT 底座运行时依赖清单（底座镜像 Layer 2 的构建输入）" \
        '#' \
        "# 来源 wheel : $1" \
        "# sha256     : $2" \
        "# 生成时间   : $3" \
        '#' \
        '# 生成方式（bin/relpack deps --write）：从载荷 wheel 的 *.dist-info/METADATA 取' \
        '#   Requires-Dist 中**不含分号**的条目（即无环境 marker / extra 的无条件运行时依赖），' \
        '#   去前缀与首尾空白后按排序落盘。' \
        '#' \
        '# 语义：本清单是载荷 wheel 声明的无条件运行时依赖；底座只装这些依赖，' \
        '#       既不装载荷 wheel 本身，也不装任何载荷内容（载荷由交付侧派生时装入）。' \
        '#' \
        '# ⚠️ 警示：本清单变化必须重发底座镜像：bin/relpack build 后重新 pack。' \
        '#    底座与载荷是两条独立发布线：交付侧派生安装载荷时走 --no-index --no-deps，' \
        '#    不会补装缺失依赖；清单变更而未重发底座，派生镜像将带缺失依赖出厂。' \
        '# ============================================================================='
}

# 头部注释块（文件开头连续的 '#' 行）
_deps_header_of() { awk '/^#/ {print; next} {exit}' "$1"; }

# 头部注释块内「来源 wheel / sha256 / 生成时间」三行按新值就地更新（只换冒号后的值，
# 保留标签与对齐）；头部缺失这三行时补写在末尾的 "# =====" 分隔线之前；其余行逐字保留。
_deps_header_render() {  # $1=输入头部文件 $2=输出文件 $3=whl 名 $4=sha256 $5=生成时间
    awk -v W="$3" -v S="$4" -v T="$5" '
        function with_val(line, val,   i) {
            i = index(line, ":")
            if (i == 0) return line " : " val
            return substr(line, 1, i) " " val
        }
        function emit_missing() {
            if (!gw) print "# 来源 wheel : " W
            if (!gs) print "# sha256     : " S
            if (!gt) print "# 生成时间   : " T
        }
        /^#/ {
            if ($0 ~ /^#[[:space:]]*来源[[:space:]]*(wheel|whl)/) { hdr[n++] = with_val($0, W); gw = 1; next }
            if ($0 ~ /^#[[:space:]]*sha256/)                       { hdr[n++] = with_val($0, S); gs = 1; next }
            if ($0 ~ /^#[[:space:]]*生成时间/)                      { hdr[n++] = with_val($0, T); gt = 1; next }
            hdr[n++] = $0; next
        }
        { exit }
        END {
            last = -1
            for (i = 0; i < n; i++) if (hdr[i] ~ /^#[[:space:]]*={3,}/) last = i
            for (i = 0; i < n; i++) {
                if (i == last) emit_missing()
                print hdr[i]
            }
            if (last < 0) emit_missing()
        }' "$1" > "$2"
}

# 重写 deps.txt：头部注释块保留（仅更新来源 wheel / sha256 / 生成时间），依赖行排序重写
write_deps_file() {  # $1=deps 文件 $2=载荷 whl；返回 2=无解压工具（未改动文件）
    local file="$1" whl="$2" name sha now dir act hdr count
    name="${whl##*/}"
    sha="$(sha256_of "$whl")" || die "未找到 sha256sum/shasum，无法计算载荷 wheel 摘要"
    now="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"   # UTC ISO8601 秒精度
    dir="$(mktemp -d "${TMPDIR:-/tmp}/relpack-deps.XXXXXX" 2>/dev/null)" || dir=""
    [ -n "$dir" ] || die "无法创建临时目录（检查 TMPDIR）：deps --write 中止，deps.txt 未改动"
    act="$dir/deps.new.body"; hdr="$dir/header.old"; hdr_new="$dir/header.new"; new="$dir/deps.new"
    if ! collect_wheel_deps "$whl" "$act"; then
        warn "未找到 unzip 或 bsdtar：无法从 $name 读出依赖集，deps --write 跳过（$file 未改动）
  处置：安装 unzip（Info-ZIP）或 bsdtar（libarchive-tar）后重试"
        rm -rf "$dir"; return 2
    fi
    if [ -f "$file" ] && [ -n "$(_deps_header_of "$file")" ]; then
        _deps_header_of "$file" > "$hdr"
    else
        _deps_default_header "$name" "$sha" "$now" > "$hdr"
    fi
    _deps_header_render "$hdr" "$hdr_new" "$name" "$sha" "$now"
    cat "$hdr_new" "$act" > "$new"
    mv -f "$new" "$file"
    count="$(wc -l < "$act" | tr -d ' ')"
    rm -rf "$dir"
    ok "依赖集已写入：products/$PRODUCT/deps.txt（$count 项无条件依赖；来源 $name）"
    info "依赖集变化必须重发底座镜像：bin/relpack build 后重新 pack"
}

# —— 3. 交付骨架 CRLF shebang 守卫 ——

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

# —— 4. release.json（schema v2）——

# $1=artifacts 目录 $2=交付版本 $3=载荷 whl 路径 $4=载荷版本 $5=载荷 sha256
# $6=底座镜像 ref $7=底座镜像 Id（无 sha256: 前缀）$8=torch 版本（空=记 null）
# $9=torch 形态（空=记 null）$10=归档文件名 $11=归档字节数 $12=归档 sha256
# 块序固定（payload 在前、archive 在后）且缩进 2 空格：读取方（客户骨架 xmnnctl）
# 按块定向取值，不依赖块序，但写入顺序一旦固定就不再变动，便于人工对拍。
write_release_manifest() {
    local artifacts="$1" ver="$2" payload="$3" payload_ver="$4" payload_sha="$5" \
          image_ref="$6" image_id="$7" torch_ver="$8" torch_flavor="$9" \
          archive="${10}" size="${11}" sha="${12}" built_at commit torch_json flavor_json
    built_at="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"   # UTC ISO8601 秒精度
    commit="$(git -C "$APP_ROOT" rev-parse HEAD 2>/dev/null || true)"
    if [ -z "$commit" ]; then commit="unknown"; fi
    if [ -n "$torch_ver" ]; then torch_json="\"$torch_ver\""; else torch_json="null"; fi
    if [ -n "$torch_flavor" ]; then flavor_json="\"$torch_flavor\""; else flavor_json="null"; fi
    cat > "$artifacts/release.json" <<EOF
{
  "schema_version": "2",
  "product": "$PRODUCT",
  "version": "$ver",
  "payload": {
    "file": "${payload##*/}",
    "version": "$payload_ver",
    "size_bytes": $(stat -c '%s' "$payload"),
    "sha256": "$payload_sha"
  },
  "image": {
    "ref": "$image_ref",
    "id": "$image_id",
    "torch_version": $torch_json,
    "torch_flavor": $flavor_json,
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

# —— 5. smoke 单步执行与失败指引 ——

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
  · 缺底座归档 → 先 bin/relpack pack（产出 artifacts/<镜像名>-base-<形态>.tar.gz）
  · 缺载荷 wheel → 先 bin/relpack stage（载荷随交付包放在 payload/ 内）
  · 载荷派生失败（pip check / 载荷守卫）→ 依赖面不一致：bin/relpack deps 校验后重建底座
  · 端口被占用 → 改 $RELEASE_NAME/.env 的 XMNN_SSH_PORT / XMNN_JUPYTER_PORT，或先 ./xmnnctl down
  · 缺 podman-compose → 在 WSL 内 pipx install podman-compose（并确认 ~/.local/bin 在 PATH）
  · Podman 后台未启动 → podman machine start"
}