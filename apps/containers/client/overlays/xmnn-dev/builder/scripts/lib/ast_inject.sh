#!/usr/bin/env bash
# ==============================================================================
# ast_inject.sh — Nuitka 编译前向 Python 包 __init__.py 注入/还原 AST 兼容层
#
# 被 build-wheel.sh source（不单独执行）。调用前需导出：
#   AST_PYTHON — 用于执行注入小脚本的解释器（固定 /opt/conda/bin/python）
#
# 安全模型（R1 F-1；2026-09-18 加固 rootless/ACL 兼容性）：
#   - 备份只复制字节、不复制元数据：**严禁 cp -p/-a/--preserve**（rootless
#     userns 只映射启动用户单个宿主 UID；外部同步树文件带含未映射 UID 的
#     POSIX ACL，cp 复制 ACL 的 setxattr 在内核态返回 EINVAL——与目标文件
#     系统无关，连容器内 overlayfs /tmp 都同样失败）；
#   - 原子落位：先复制到 ${backup}.tmp.<pid> 再 mv -f，杜绝半写备份；cp
#     失败立即 rm tmp，ast_inject 入口幂等清扫同 tag 陈旧 tmp；
#   - 原 inode 还原：ast_restore 以 cat 内容回写覆盖原 inode（不 mv 替换），
#     外部源码文件的属主/模式/ACL 在注入-还原全程不变；
#   - 注入前状态机：若文件已含 PREAMBLE（上次被 SIGKILL/OOM 杀掉、trap 无法
#     运行的残留态）——备份仍在则先自愈还原；备份丢失则 Exit 2 要求人工
#     `git checkout`，**绝不覆盖任何文件**（避免干净备份被污染版顶替）；
#   - ast_inject 幂等：残留态重跑可安全收敛；正常态备份/注入只发生一次；
#   - ast_restore 幂等：备份不存在即为 no-op，供 EXIT trap 反复调用；内容
#     回写失败时保留备份交由重跑收敛，绝不先删备份。
# ==============================================================================

AST_PREAMBLE_BEGIN='# === XMNN BOOTSTRAP ==='
AST_PREAMBLE_END='# === END XMNN BOOTSTRAP ==='
AST_PREAMBLE_BODY='import ast as _ast
if not hasattr(_ast, "NameConstant"):
    class _NameConstant(_ast.Constant):
        def __new__(cls, value=None, **kwargs):
            return super().__new__(cls, value=value, **kwargs)
    _ast.NameConstant = _NameConstant
if not hasattr(_ast, "Num"):
    class _Num(_ast.Constant):
        def __new__(cls, n=None, **kwargs):
            return super().__new__(cls, value=n, **kwargs)
    _ast.Num = _Num
if not hasattr(_ast, "Str"):
    class _Str(_ast.Constant):
        def __new__(cls, s="", **kwargs):
            return super().__new__(cls, value=s, **kwargs)
    _ast.Str = _Str
if not hasattr(_ast, "Bytes"):
    class _Bytes(_ast.Constant):
        def __new__(cls, s=b"", **kwargs):
            return super().__new__(cls, value=s, **kwargs)
    _ast.Bytes = _Bytes
if not hasattr(_ast, "Index"):
    class _Index(_ast.expr):
        _fields = ("value",)
        def __init__(self, value, **kwargs):
            self.value = value
            super().__init__(**kwargs)
    _ast.Index = _Index
if not hasattr(_ast, "ExtSlice"):
    class _ExtSlice(_ast.expr):
        _fields = ("dims",)
        def __init__(self, dims=None, **kwargs):
            self.dims = dims if dims is not None else []
            super().__init__(**kwargs)
    _ast.ExtSlice = _ExtSlice
'

ast_has_preamble() {
    grep -qF "$AST_PREAMBLE_BEGIN" "$1" 2>/dev/null
}

# ast_restore <init_file> <backup_file> —— 幂等；无备份则 no-op 返回 1。
# 信息一律走 stderr：ast_inject 的 stdout 契约是「仅输出 backup 路径」，
# 本函数在 ast_inject 的自愈分支内被调用，stdout 污染会破坏 $(ast_inject)。
ast_restore() {
    local init_file="$1"
    local backup="$2"
    if [ -z "${init_file:-}" ] || [ -z "${backup:-}" ] || [ ! -f "$backup" ]; then
        return 1
    fi
    # 内容回写到原 inode（不 mv 替换）：保留外部源码文件的属主/模式/ACL。
    # 回写失败（磁盘满等）时保留 backup，由调用方/重跑自愈矩阵收敛。
    if ! cat -- "$backup" > "$init_file"; then
        echo "  [RESTORE-FAIL] 内容回写失败，备份已保留: $backup" >&2
        return 1
    fi
    rm -f -- "$backup"
    echo "  [RESTORE] $init_file" >&2
    return 0
}

# ast_inject <init_file> <tag> —— 成功时 stdout 输出 backup 路径；
# 残留不可自愈时 return 2（不覆盖任何文件）。
# 自愈矩阵（覆盖 SIGKILL/OOM 的所有残留形态）：
#   marker 在 + bak 在      → 上次注入后被杀，bak 干净 → 还原后继续
#   marker 在 + 无 bak      → 无法判定干净版本 → Exit 2，要求 git checkout
#   marker 不在 + bak 在    → 注入器截断窗口残留（init 空/半写）→ bak 干净，还原后继续
#   marker 不在 + 无 bak    → 正常态 → 备份后注入
ast_inject() {
    local init_file="$1"
    local tag="$2"
    local backup="${init_file}.bak_${tag}"
    local tmp_backup="${backup}.tmp.$$"
    local _stale

    if [ ! -f "$init_file" ]; then
        echo "  [FATAL] 待注入文件不存在: $init_file" >&2
        return 2
    fi

    # 清扫同 tag 的陈旧 tmp（历史失败/SIGKILL 泄漏）；同 tag 无并发，
    # 前缀含完整绝对路径，不会波及其他包的备份。
    for _stale in "${backup}.tmp."*; do
        [ -e "$_stale" ] && rm -f -- "$_stale"
    done

    if ast_has_preamble "$init_file"; then
        if [ -f "$backup" ]; then
            echo "  [RECOVER] 检测到上次残留的注入态且备份在，先自愈还原: $init_file" >&2
            ast_restore "$init_file" "$backup" || true
        else
            echo "  [FATAL] $init_file 已含 AST PREAMBLE 但备份 $backup 缺失。" >&2
            echo "          上次可能被 SIGKILL/OOM 中断；为避免用污染版覆盖干净文件，已停止。" >&2
            echo "          请人工确认后还原，例如：git -C $(dirname "$init_file") checkout -- $init_file" >&2
            return 2
        fi
    elif [ -f "$backup" ]; then
        echo "  [RECOVER] 检测到截断残留（备份在但无注入标记），用干净备份自愈还原: $init_file" >&2
        ast_restore "$init_file" "$backup" || true
    fi

    # 字节级原子备份：普通 cp（不带 -p，理由见文件头安全模型）→ 同目录 mv。
    # cp 失败立即清 tmp 并 return 2，绝不让泄漏文件残留在外部源码树。
    if ! cp -- "$init_file" "$tmp_backup"; then
        echo "  [FATAL] 创建字节备份失败: $init_file -> $tmp_backup" >&2
        rm -f -- "$tmp_backup" 2>/dev/null || true
        return 2
    fi
    mv -f -- "$tmp_backup" "$backup"

    "$AST_PYTHON" - "$init_file" <<PYEOF
import sys
init_file = sys.argv[1]
preamble = '''$AST_PREAMBLE_BEGIN
$AST_PREAMBLE_BODY$AST_PREAMBLE_END

'''
original = open(init_file, 'r', encoding='utf-8').read()
if '$AST_PREAMBLE_BEGIN' not in original:
    open(init_file, 'w', encoding='utf-8').write(preamble + original)
print('  [INJECT] AST PREAMBLE injected into %s ($tag)' % init_file, file=sys.stderr)
PYEOF
    printf '%s' "$backup"
}
