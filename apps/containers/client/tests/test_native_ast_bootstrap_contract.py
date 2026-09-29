"""AST 启动钩子「提供者—守卫」契约单测（回归 sc-20260928-native-build-cu130）。

故障形态：``install-ast-bootstrap.sh`` 与 ``smoke/_toolchain_guards.py`` §11
曾按 CPython 3.14 文档移除全集断言五名（含 ``Ellipsis``），而
``builder/_xmnn_bootstrap.py`` 与生态四份真源（external/chaos 下 ai/sdk、
xmnn-whl-builder、xmtools、docker preamble）只恢复四名——容器内 Python
3.14.7 实测 ``ast.Ellipsis`` 恒为 False，导致镜像 STEP 20/21 构建期硬失败
（``AssertionError: ast aliases missing``）。``Ellipsis`` 无运行时消费者
（tvm 上游测试主动 delattr 五名仍通过），错在守卫过度规约而非提供者缺失。

本测试把契约锁成三条不变式（daemon-free，纯文本/AST 解析，双平台可跑）：

1. 两处守卫清单（shell 安装验证 + smoke §11）逐字一致；
2. 守卫集 == 哨兵四名且 ⊆ 提供者实际恢复集（钩子不恢复的名字永远不许进守卫）；
3. ``Ellipsis`` 显式排除（防止后来者按文档全集再次"补全"）。
"""

import ast
import re
from pathlib import Path

CLIENT_ROOT = Path(__file__).resolve().parents[1]
OVERLAY = CLIENT_ROOT / "overlays" / "native-dev"
BOOTSTRAP = OVERLAY / "builder" / "_xmnn_bootstrap.py"
INSTALL_SCRIPT = OVERLAY / "scripts" / "install-ast-bootstrap.sh"
SMOKE_GUARDS = OVERLAY / "smoke" / "_toolchain_guards.py"

# stock CPython 3.14.7 实测：四名全缺、钩子恢复后全有；
# Index/ExtSlice 原生仍存（无哨兵价值）；Ellipsis 被移除但无恢复亦无消费。
SENTINEL_CONTRACT = frozenset({"NameConstant", "Num", "Str", "Bytes"})

_AST_LEGACY_NAMES = (
    "NameConstant", "Num", "Str", "Bytes", "Ellipsis", "Index", "ExtSlice",
)


def _provider_restored_names() -> set[str]:
    """从 bootstrap 源码提取模块级 ``ast.<Name> = ...`` 实际补丁名。"""
    tree = ast.parse(BOOTSTRAP.read_text(encoding="utf-8"))
    restored: set[str] = set()
    for node in tree.body:
        # if not hasattr(ast, "X"):
        #     class _X(ast.Constant): ...
        #     ast.X = _X
        if not isinstance(node, ast.If):
            continue
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Assign)
                and len(sub.targets) == 1
                and isinstance(sub.targets[0], ast.Attribute)
                and isinstance(sub.targets[0].value, ast.Name)
                and sub.targets[0].value.id == "ast"
                and sub.targets[0].attr in _AST_LEGACY_NAMES
            ):
                restored.add(sub.targets[0].attr)
    return restored


def _shell_guard_names() -> set[str]:
    """提取 install-ast-bootstrap.sh 内 ``for n in (...)`` 断言名清单。"""
    text = INSTALL_SCRIPT.read_text(encoding="utf-8")
    match = re.search(r'hasattr\(ast,\s*n\).*?\(([^)]*)\)', text, re.DOTALL)
    assert match, "未在安装脚本中找到 ast 哨兵断言元组"
    return set(re.findall(r'"([A-Za-z]+)"', match.group(1)))


def _smoke_guard_names() -> set[str]:
    """提取 smoke/_toolchain_guards.py 的 ``_AST_SENTINELS`` 字面量。"""
    tree = ast.parse(SMOKE_GUARDS.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "_AST_SENTINELS"
                    for t in node.targets)
            and isinstance(node.value, (ast.Tuple, ast.List))
        ):
            return {
                elt.value
                for elt in node.value.elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            }
    raise AssertionError("未在 smoke 守卫中找到 _AST_SENTINELS 定义")


def _smoke_main_ast_code() -> str:
    """求值 smoke 守卫里发给 main 解释器的 ``main_ast_code`` 拼接表达式。

    必须真实求值 + compile()：隐式字符串拼接里的 f-string 括号一旦写错
    （少一个 ``)``），静态文本审查无法发现，构建期才以
    ``SyntaxError: '(' was never closed`` 爆炸（本回归第二次失败的形态）。
    """
    sentinels = tuple(sorted(_smoke_guard_names()))
    tree = ast.parse(SMOKE_GUARDS.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "_AST_SENTINELS"
                    for t in node.targets)
        ):
            # 用文件内真实元组（含真实顺序），而非排序集
            sentinels = ast.literal_eval(node.value)
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "main_ast_code"
                    for t in node.targets)
        ):
            return eval(  # noqa: S307 - 仅求值仓库内受控的字符串字面量拼接
                compile(ast.Expression(node.value), "<main_ast_code>", "eval"),
                {"_AST_SENTINELS": sentinels, "repr": repr},
            )
    raise AssertionError("未在 smoke 守卫中找到 main_ast_code 定义")


def test_provider_restores_four_removed_names():
    restored = _provider_restored_names()
    assert SENTINEL_CONTRACT <= restored, (
        f"bootstrap 未恢复哨兵四名，实际恢复：{sorted(restored)}"
    )


def test_provider_does_not_restore_ellipsis():
    # 契约事实（2026-09-28 容器实测 + 生态四份真源一致）：Ellipsis 不在
    # 恢复集。若未来生态真源开始恢复 Ellipsis，应先改本测试再改守卫——
    # 即"扩提供者先于扩守卫"，禁止反向过度规约。
    assert "Ellipsis" not in _provider_restored_names()


def test_shell_and_smoke_guard_lists_are_identical():
    assert _shell_guard_names() == _smoke_guard_names(), (
        "安装脚本与 smoke §11 的 ast 哨兵清单漂移"
    )


def test_guard_set_equals_contract_and_subset_of_provider():
    guard = _smoke_guard_names()
    assert guard == set(SENTINEL_CONTRACT), (
        f"守卫集 {sorted(guard)} != 哨兵契约 {sorted(SENTINEL_CONTRACT)}；"
        "新增名字前须先证明 bootstrap 恢复它且存在运行时消费者"
    )
    assert guard <= _provider_restored_names()


def test_ellipsis_explicitly_excluded_from_guards():
    assert "Ellipsis" not in _shell_guard_names()
    assert "Ellipsis" not in _smoke_guard_names()


def test_main_ast_code_compiles_and_matches_contract():
    code = _smoke_main_ast_code()
    compile(code, "<main_ast_code>", "exec")  # 括号失衡在此即 SyntaxError
    for name in SENTINEL_CONTRACT:
        assert name in code, f"main_ast_code 未覆盖哨兵 {name}"
    assert "Ellipsis" not in code
