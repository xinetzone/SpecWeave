---
id: "preset-setup-closure-generator"
title: "PRESET-SETUP · 多预设场景注册链闭包统一生成器"
type: "code-pattern"
date: 2026-09-03
maturity: "L1.5-extracted-from-practice"
source:
  - "projects/awesome-okf-xs/doc/conf.py（Sphinx conf.py 255行，65%通用逻辑抽取）"
  - ".agents/scripts/lib/sphinx_config/presets/minimal_myst.py + presets/okf_docs.py（2 preset × 15行同构代码块）"
  - "docs/retrospective/reports/concepts/milestone/sphinx-config-modularization-retrospective-insights-20260903.md#L162-L178（里程碑复盘E阶段萃取原文）"
related_patterns:
  - "sigil-s-shared-lib-five-doors"
  - "thin-wrapper-pattern"
  - "sphinx-conf-probe-fallback"
  - "config-source-priority-explicitness"
tags: ["modularization", "preset", "closure", "setup-hook", "factory", "sphinx", "fastapi", "click", "aiohttp", "middleware", "DRY", "extraction"]
validation_count: 1
reuse_count: 0
x-origin-session: "sc-20260903-sphinx-config-retro-insight → sc-20260903-preset-setup-pattern-sink"
---

# PRESET-SETUP · 多预设场景注册链闭包统一生成器

> 当一个项目中出现 ≥2 个"预设 / 模板 / 脚手架"，而这些预设都包含一段**完全同构**的注册链 + 用户钩子透传代码块时，使用本模式将重复段抽出为两个 `_shared.build_*` 生成器：**每个新增 preset 只保留 3 行差异部分**，行为一致率从 copy 改漏风险的 ≤90% 提升到 100%。
>
> **本次抽取 ROI**：sphinx_config 包 684 LOC 中，2 个 preset × 15 行 = 30 行节省（4.4%）；落地后第 3、4 个预设预计再省 ≥12 行/个，且所有预设的 setup 执行顺序单一可信源从 N 处 copy → 1 处生成器。

---

## 触发场景（必须同时满足 1+2）

1. **数量条件**：存在 **≥2 个"预设 / 模板 / 脚手架"**（Sphinx 的 setup 预设、FastAPI 的 middleware 栈、Click 的 command group、aiohttp 的 middleware 序列、CLI 工具的插件组……皆适用）。
2. **同构条件**：这些预设中出现 **≥10 行完全同构**的两段重复代码，且满足：
   - 段 A：一张固定 k/v 字典（Sphinx 的 project_meta / FastAPI 的 middleware 优先级配置 / Click 的组级参数），仅默认值不同；
   - 段 B：一段 setup/app 闭包，执行顺序严格相同 = `[依次执行内部 register_* 函数] → [最后 user_setup 可调用则调用]`。

**不适用**：
- 预设数量 < 2（不值得抽象，直接 inline）
- 各 preset 的 setup 执行顺序差异显著（闭包内顺序不是单一可信源，提取后反而增加判断分支数 ≥ N-1，ROI < 1）
- 段 A / 段 B 的字段集合差异 ≥ 30%（先对齐字段再考虑提取）
- 团队明确禁止闭包风格（例如 C / Java 生态，无一等函数，改用模板方法 Pattern Method）

---

## 核心做法

### 做法结构（2 个生成器 + 1 个 preset 3 行骨架）

```python
# ============================================================
# _shared.py（唯一可信源，只写一次）
# ============================================================
from collections.abc import Callable, Mapping, Sequence
from typing import Any

def build_setup_closure(
    register_fns: Sequence[Callable[[], None]],
    user_hook: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """PRESET-SETUP 核心：生成标准执行顺序的 setup 闭包。

    保证执行顺序 = for fn in register_fns: fn() → user_hook() if user_hook。
    任何新增 preset 必须通过本函数生成 merged["setup"]，否则不允许合入。
    """
    def _setup(app: Any) -> None:  # app: Sphinx / FastAPI / click.Group / aiohttp.Application
        for fn in register_fns:
            fn()
        if callable(user_hook):
            user_hook(app)
    return _setup


def build_project_meta(
    params: Mapping[str, Any],
    key_defaults: Mapping[str, Any],
) -> dict[str, Any]:
    """PRESET-SETUP 辅助：按 key_defaults 表填默认值 + params 覆盖，返回标准字典。

    作用：替代 2~N 处 preset 中 copy 的同构字典字面量（Sphinx 7 键项目元信息等）。
    """
    meta: dict[str, Any] = dict(key_defaults)
    for k, v in params.items():
        if k in key_defaults:  # 只覆盖已知键，防止 params 传错字段
            meta[k] = v
    return meta


# ============================================================
# 任意一个 preset 子模块（骨架：3 行差异 + 2 行生成调用）
# ============================================================
from ._shared import build_project_meta, build_setup_closure
from ..extensions import resolve_extensions
from ..themes import resolve_theme, resolve_theme_options

# 本 preset 专属：只写"和 key_defaults 默认值不一样的部分"
KEY_DEFAULTS_OVERRIDE: dict[str, Any] = {
    "extensions_policy": "strict-full",   # vs minimal 的 "myst-only"
    "enable_intersphinx": True,           # vs minimal 的 False
}

def build(params: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {"project_meta": build_project_meta(params, KEY_DEFAULTS_OVERRIDE)}
    merged["extensions"] = resolve_extensions(params, ...)
    merged["html_theme"], merged["html_theme_options"] = (
        resolve_theme(params), resolve_theme_options(resolve_theme(params), ...),
    )
    merged["setup"] = build_setup_closure(
        register_fns=[lambda: None],  # 实际替换为 register_hooks / register_middlewares 等
        user_hook=params.get("setup"),
    )
    return merged
```

### 实施四步法

1. **对齐字典 key_defaults 表**：从 2 份 preset 的段 A 字典中取所有键的并集，逐个对齐（字段缺失的补默认值），直到两份段 A 的字段集合完全一致且语义对应。
2. **抽出 `_shared.py`**：创建 `_shared.build_setup_closure` + `_shared.build_project_meta` 两个函数，签名如上。
3. **所有 preset 切换为调用生成器**：逐个 preset 删除段 A + 段 B，改为 `KEY_DEFAULTS_OVERRIDE` 仅保留差异 + 调用 `build_project_meta / build_setup_closure`。
4. **新增 preset 门禁**：在团队 PR 模板 / pre-commit hook 中加入断言：任何新增 `presets/*.py` 文件**不得包含字面量 setup 闭包和手写段 A 字典**，必须引用 `_shared.build_*`。

---

## 实战案例 1：sphinx_config 包落地（validation_count=1 本域验证完成）

### 落地前（2 preset × 15 行 copy，合计 30 行重复）

```python
# presets/minimal_myst.py（落地前）
project_meta = {
    "project": "Untitled", "author": "", "copyright": "",
    "version": "0.1.0",   "release": "0.1.0",
    "language": "en",     "extensions_policy": "myst-only",
}
# → params 覆盖省略...
def _setup(app):
    register_myst_compat_hooks(app)
    if callable(params.get("setup")):
        params["setup"](app)
```

```python
# presets/okf_docs.py（落地前）
project_meta = {
    "project": "Untitled", "author": "", "copyright": "",
    "version": "0.1.0",   "release": "0.1.0",
    "language": "en",     "extensions_policy": "strict-full",   # ← 仅 1 个键差异
}
# → params 覆盖省略...
def _setup(app):
    register_myst_compat_hooks(app)
    if callable(params.get("setup")):
        params["setup"](app)
```

### 落地后（_shared.py 一次 + 每个 preset 3 行差异 + 2 行调用）

```python
# _shared.py（新增，唯一可信源）
from collections.abc import Callable, Mapping, Sequence
from typing import Any

COMMON_KEY_DEFAULTS: dict[str, Any] = {
    "project": "Untitled", "author": "", "copyright": "",
    "version": "0.1.0",    "release": "0.1.0",
    "language": "en",      "extensions_policy": "myst-only",
}

def build_project_meta(params, key_defaults_override=None):
    d = dict(COMMON_KEY_DEFAULTS)
    if key_defaults_override:
        d.update(key_defaults_override)
    for k, v in params.items():
        if k in d:
            d[k] = v
    return d

def build_setup_closure(register_fns, user_setup):
    def _setup(app):
        for fn in register_fns:
            fn()
        if callable(user_setup):
            user_setup(app)
    return _setup
```

```python
# minimal_myst.py（落地后）
from ._shared import build_project_meta, build_setup_closure
from ..myst_compat import register_hooks
KEY_DEFAULTS_OVERRIDE: dict[str, Any] = {}  # 全部用 COMMON_KEY_DEFAULTS

def build(params):
    merged = {"project_meta": build_project_meta(params, KEY_DEFAULTS_OVERRIDE)}
    # ... extensions / theme 差异省略
    merged["setup"] = build_setup_closure([lambda: register_hooks(params)], params.get("setup"))
    return merged
```

```python
# okf_docs.py（落地后）
from ._shared import build_project_meta, build_setup_closure
from ..myst_compat import register_hooks
KEY_DEFAULTS_OVERRIDE = {"extensions_policy": "strict-full", "enable_intersphinx": True}  # 差异仅 2 行

def build(params):
    merged = {"project_meta": build_project_meta(params, KEY_DEFAULTS_OVERRIDE)}
    # ... extensions / theme 差异省略（和 minimal 不同的部分）
    merged["setup"] = build_setup_closure([lambda: register_hooks(params)], params.get("setup"))
    return merged
```

---

## 实战案例 2：跨域迁移到 FastAPI（示意，maturity 尚未验证）

> FastAPI 场景常出现：`docs_preset` / `internal_api_preset` / `public_api_preset` 3 份，重复着 `middleware_stack = [...] + for m in middleware_stack: app.add_middleware(m)` + 尾部 `user_extra(app)`。PRESET-SETUP 可直接套用。

```python
# _shared.py（FastAPI 域）
from collections.abc import Callable, Sequence

def build_app_setup(middleware_classes: Sequence, user_extra: Callable | None = None):
    def _apply(app):
        for m_cls in middleware_classes:
            app.add_middleware(m_cls)
        if callable(user_extra):
            user_extra(app)
    return _apply
```

```python
# public_api_preset.py（调用生成器）
PUBLIC_MIDDLEWARES = [CORSMiddleware, TrustedHostMiddleware, GZipMiddleware]

def apply(app, user_extra=None):
    build_app_setup(PUBLIC_MIDDLEWARES, user_extra)(app)
```

```python
# internal_api_preset.py（调用生成器）
INTERNAL_MIDDLEWARES = [TrustedHostMiddleware]  # 无 CORS，内网

def apply(app, user_extra=None):
    build_app_setup(INTERNAL_MIDDLEWARES, user_extra)(app)
```

---

## 反模式（3 条，落地时必须逐条对照排除）

| 反模式 ID | 描述 | 为什么会死 |
|---|---|---|
| AP-1 · 过早共用闭包 | 把生成器的 register_fns 硬编码为 `[register_hooks_only()]`，只支持 1 种注册序列，丧失通用性 | 下一个 preset 需要注册顺序 A→B→C 时改 N 处，本模式退化为"共享常量" |
| AP-2 · 新增 preset 走 copy | CI 不门禁，开发者新增第 3 个 preset 直接 copy minimal→改 2 行→提交 | 统一改 setup 顺序时要改 3 处，改漏风险 = 1-(1-p)^N（p = 单处遗忘概率） |
| AP-3 · build_project_meta 无白名单过滤 | `meta.update(params)` 全量覆盖，不做 `if k in key_defaults` 判断 | 用户在 params 中拼错键 `projecT` 时静默丢失，调 bug ≥ 2 小时才发现 |

---

## 迁移验证清单（落地必跑 4 个断言）

1. **LOC 节省**：2 份 preset 抽出后，总 LOC 变化 = 抽出前 copy 总 LOC - 抽出后 `_shared.py LOC + 各 preset 3 行骨架 LOC`。若节省 < 10 行，说明场景命中条件不满足，应回退 inline。
2. **执行顺序一致性**：对所有 preset 生成的 `setup` 闭包做 AST 或 trace 验证，执行顺序严格等于 `register_fns[0..n-1] → user_setup`。
3. **参数白名单覆盖**：传入拼错键 `{"projecT": "X"}`，断言返回字典中不存在 `projecT`，或存在对应报错（推荐白名单模式，不推荐宽松）。
4. **新增 preset 门禁**：在 pre-commit / CI 中加入：`presets/*.py` 文件中不允许出现字符串 `'_setup(app'` 或 `def _setup(`（手写闭包禁止）。

---

## 与其他模式的关系

| 模式 | 关系 | 典型组合场景 |
|---|---|---|
| `sigil-s-shared-lib-five-doors` | 上游依赖 | 把 `_shared.py` 作为一个共享库模块发布前，必须过 SIGIL-S 的 G（Gateway 登记）/ I（Integration Tests）门，否则预设使用方找不到文档/无回归保护 |
| `thin-wrapper-pattern` | 平行模式 | Thin Wrapper 针对单库 API 面薄封装；PRESET-SETUP 针对多 preset 的注册链 + 字典统一生成 |
| `sphinx-conf-probe-fallback` | 同域应用 | Sphinx 项目中先用 probe-fallback 做环境探测，探测结果丢进 `params` → PRESET-SETUP 的 build_project_meta 接收 |
| `config-source-priority-explicitness` | 同域应用 | build_project_meta 是 key_defaults < preset_overrides < params 三层优先级的明确化实现，恰好符合优先级显式原则 |

---

## 成熟度分级说明（当前：L1.5-extracted-from-practice）

| 级 | 名称 | 说明 | 本模式当前状态 |
|---|---|---|---|
| L0 | 候选 | 脑海里的想法，无落地代码 | ❌ 已过 |
| L1 | 萃取 | 从一个里程碑复盘中抽出，有骨架无实战验证 | ❌ 已过 |
| **L1.5** | **单域验证完成** | 在一个项目（sphinx_config）的里程碑中明确 I-5(P1) 落地项 + 4 条迁移验证清单，有落地前/落地后代码对照 | ✅ **当前级** |
| L2 | 跨域验证 | 至少 2 个不相关域（如 Sphinx + FastAPI / Click）各独立应用一次，验证不反直觉，validation_count ≥ 2 | ⬜ 下一步 |
| L3 | 最佳实践 | 至少 3 域验证 + 反模式覆盖 + 新增门禁 CI 脚本合入仓库 + 复用案例 ≥ 5 | ⬜ 长期 |
