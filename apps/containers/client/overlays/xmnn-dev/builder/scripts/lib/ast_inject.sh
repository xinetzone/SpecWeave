#!/usr/bin/env bash
# ==============================================================================
# ast_inject.sh — Nuitka 编译前向 Python 包 __init__.py 注入/还原 AST 兼容层
#
# 被 build-wheel.sh source（不单独执行）。调用前需导出：
#   AST_PYTHON — 用于执行注入小脚本的解释器（固定 /opt/conda/bin/python）
#
# 安全模型（R1 F-1 修复）：
#   - 备份原子化：先复制到 ${backup}.tmp.<pid> 再 mv -f，杜绝半写备份；
#   - 注入前状态机：若文件已含 PREAMBLE（上次被 SIGKILL/OOM 杀掉、trap 无法
#     运行的残留态）——备份仍在则先自愈还原；备份丢失则 Exit 2 要求人工
#     `git checkout`，**绝不覆盖任何文件**（避免干净备份被污染版顶替）；
#   - ast_inject 幂等：残留态重跑可安全收敛；正常态备份/注入只发生一次；
#   - ast_restore 幂等：备份不存在即为 no-op，供 EXIT trap 反复调用。
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
    if [ -n "${init_file:-}" ] && [ -n "${backup:-}" ] && [ -f "$backup" ]; then
        mv -f "$backup" "$init_file"
        echo "  [RESTORE] $init_file" >&2
        return 0
    fi
    return 1
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

    if [ ! -f "$init_file" ]; then
        echo "  [FATAL] 待注入文件不存在: $init_file" >&2
        return 2
    fi

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

    # 原子备份（临时文件 + mv），避免半写备份
    cp -p "$init_file" "${backup}.tmp.$$"
    mv -f "${backup}.tmp.$$" "$backup"

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
