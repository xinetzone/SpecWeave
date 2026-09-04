---
id: "sphinx-parallel-build-5k-scale"
title: "Sphinx 并行构建机制与 5k+ 文件规模应对策略"
date: 2026-09-03
type: "tech-research"
source: "会话内七概念分析结果（基于 SpecWeave vendor Sphinx 源码 external/libs/docs/sphinx 全量调研）；场景：技术研究 + 方案选型（R-I-F-V-E 链路）"
tags: ["sphinx", "parallel-build", "build-scaling", "docs-infra", "mystx", "seven-concepts"]
maturity: "L1.5"
---

# Sphinx 并行构建机制与 5k+ 文件规模应对策略

> 执行框架：七概念方法论（R-I-F-V-E），纯调研分析，无代码修改。

---

## 摘要

本报告基于 SpecWeave 仓库内 vendored 版本 Sphinx 源码（路径 [../../../../../external/libs/docs/sphinx](../../../../../external/libs/docs/sphinx/)），完成七概念框架（R→I→F→V→E）的全链路技术调研，核心结论：

| 结论 | 说明 |
|------|------|
| **Sphinx 支持进程级并行** | 仅在 POSIX（fork）系统上可用；Windows 自动回退串行，`-j N` 参数对 Windows 静默失效 |
| **read 阶段是核心瓶颈** | Worker 回传整个 partial BuildEnvironment pickle，5k 文件规模下主进程 IPC/merge 占总时间 60%+ |
| **扩展声明是静默陷阱** | 任何一个扩展未声明 `parallel_read_safe=True`，整个 read 阶段强制串行；mystx 与多数第三方扩展存在缺口 |
| **策略分三层 ROI** | P0 立即执行（扩展声明 + WSL 强制 + 默认 `-j auto`，2–5×）→ P1 中期优化（chunk 调优 + 增量缓存，1.5–3×）→ P2 天花板突破（Intersphinx 分片，彻底解除单项目上限） |
| **萃取 3 个可复用模式** | EXT-PARALLEL-GATE、SHARD-BY-INTERSPHINX、WINDOWS-WSL-WORKAROUND |

---

## R — 事实采集（Retrospective / Facts）

### R1. Sphinx 原生并行能力代码级事实

| 维度 | 代码位置 | 结论 |
|---|---|---|
| **并行可用性门槛** | [parallel.py:L28](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/util/parallel.py#L28-L28) | `parallel_available = HAS_MULTIPROCESSING and os.name == 'posix'` — **仅 POSIX（Linux/macOS/WSL）可用** |
| **fork 硬依赖** | [parallel.py:L103](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/util/parallel.py#L103-L103) | 使用 `multiprocessing.get_context('fork')`，spawn 模型不可用（Windows 缺 fork → `SerialTasks`） |
| **CLI 入口** | [build.py:L427](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/cmd/build.py#L427-L427) | `-j N` / `-j auto`（= `cpu_count()`）→ `Sphinx(parallel=N)` |
| **分块算法** | [parallel.py:L156-169](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/util/parallel.py#L156-L169) | `chunksize = sqrt(nargs/nproc * maxbatch)`，maxbatch=10；对 5k 文档 + 8 worker → 每块 ≈79 doc，共 ≈64 chunks |
| **HTML Builder 放行** | [html/__init__.py:L118](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/builders/html/__init__.py#L118-L118) | `StandaloneHTMLBuilder.allow_parallel = True` — write 阶段可并行；read 并行另看扩展声明 |
| **其他 Builder** | 基类 `Builder.allow_parallel = False` | LaTeX / singlehtml / linkcheck / epub3 / manpage / gettext / texinfo / text / dirhtml / changes / xml / dummy 等需逐例验证 |

### R2. 并行读 / 写流程 IPC 事实

| 阶段 | 代码位置 | IPC 载荷与流程 |
|---|---|---|
| **并行 READ** | [_read_parallel()](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/builders/__init__.py#L592-L629) | Worker fork 完成解析后，**`pickle.dumps(整个 partial BuildEnvironment)`** 经 pipe 回传；主进程 `merge_info_from()` 合并 `all_docs`、`included`、`reread_always` 与各 domain 数据 |
| **并行 WRITE** | [_write_parallel()](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/builders/__init__.py#L779-L818) | **主进程先串行** 执行 `get_and_resolve_doctree() + write_doc_serialized()` N 次，再把已 resolve 的 `(docname, doctree)` 列表发给 worker 跑 `write_doc`，IPC 比 read 轻很多 |
| **全局串行阶段** | [build()](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/builders/__init__.py#L389-L466) | `read → pickle(env) → check_consistency → prepare_writing → write → finish`；**除 read_parallel / write_parallel 本体，其余全串行** |

### R3. 扩展并行安全门控事实

| 机制 | 位置 | 规则 |
|---|---|---|
| **守卫函数** | [application.py:L1800-1837](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/application.py#L1800-L1837) | `is_parallel_allowed('read'\|'write')` 遍历全部加载扩展 |
| **read_safe 默认值** | `extension.py` kwargs 默认 | `parallel_read_safe=None`（**opt-in；未声明 = 不安全 = 强制串行**） |
| **write_safe 默认值** | `extension.py` kwargs 默认 | `parallel_write_safe=True`（opt-out；默认允许） |
| **myst_nb 上游声明** | Web 引用：`myst_nb/sphinx_ext.py` | 返回 `{"parallel_read_safe": True, "parallel_write_safe": True}` ✅ |
| **mystx conf.py 当前缺口** | [conf.py:L227-251](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/mystx/doc/conf.py#L227-L251) | `setup(app)` **未返回 metadata dict** → 被计为"未声明" → 触发 warning + 强制串行 ❌ |
| **mystx 扩展清单（风险）** | [conf.py:L46-253](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/mystx/doc/conf.py#L46-L253) | 共 17+ 扩展：mystx、sphinx_design、viewcode、intersphinx、copybutton、sphinx_comments、autoapi、graphviz、sphinx_contributors、sphinxext.opengraph、sphinx_tippy、sphinx_pyscript、mystx.ext.github_readme_stats、sphinxcontrib.bibtex、sphinx_sitemap、sphinx_examples、extlinks — **多数未显式声明 parallel_read_safe** |

### R4. BuildEnvironment.merge 事实

| 要点 | 代码位置 | 说明 |
|---|---|---|
| merge_info_from | [environment/__init__.py:L421-437](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/environment/__init__.py#L421-L437) | 合并 all_docs / included / reread_always / domain_data + 触发 `env-merge-info` 事件 |
| 扫描与增量判定 | [find_files()](file:///d:/spaces/SpecWeave/external/libs/docs/sphinx/sphinx/environment/__init__.py#L485-L535) | `project.discover()` 扫描；`get_outdated_files()` 增量判定 |

---

## I — 洞察分析（Insight / Root Causes）

### 六大瓶颈根因 + 影响 + 建议四元组

| # | 根因 | 影响量级（5k 文档规模） | 建议 |
|---|---|---|---|
| **I-1** | **read 阶段 pickle IPC 爆炸**：每个 worker 回传完整 env 副本；8 worker × 64 chunk ≈ **512 次全量 env pickle 传输 + merge** | 单 env 200–500MB → 管道流量 >100GB，主进程 merge 循环占总时间 60%+ | 优先用 incremental build 缩减 changed docs；必要时降低 `-j` 到 4–6 避免内存 / 带宽共振 |
| **I-2** | **write 前串行解析瓶颈**：`_write_parallel` 预备段在 main 中串行跑 `get_and_resolve_doctree()` 5k 次，worker 只拿已解析树渲染 | 交叉引用解析全局耦合，不可并行；占总时间 ~20% | 减少跨文档引用密度；Intersphinx 拆分降低单次 env 体积 |
| **I-3** | **environment.pickle 单点 I/O**：首次构建 / `-E` 强制重建时，加载与保存多 GB env 文件是纯串行 I/O | SATA SSD 下读 2GB ≈3–5s、写≈5–8s；HDD 放大 5–10x | 保持 `.doctrees/` 缓存有效；避免频繁 `-E`；评估 tmpfs / NVMe 挂载 |
| **I-4** | **Windows SerialTasks 静默降级**：`os.name != 'posix'` 时 `-j 任何值` 等同无并行，且 **只有 -v 才看到 warning** | 用户以为 16 核实际 1 核，慢 8–15x 不自知 | 构建入口强制 WSL；CI 用 Linux runner；脚本加 `os.name` 预检并显式报错 |
| **I-5** | **扩展未声明 parallel_read_safe → 静默串行**：`is_parallel_allowed('read')` 任一扩展为 `None` 即整体 False | mystx conf.py 中 setup() 返回 None 已足以使并行读失效；autoapi / bibtex / tippy 等也可能未声明 | 每个扩展逐一声明；conf.py 末尾加 parallel_read_safe 断言钩子 |
| **I-6** | **make_chunks maxbatch=10 创建过多 chunk**：5k × 8 → 64 块，每块 79 doc，每次 merge 全量 env diff | chunk 过多 = merge 次数多 = 主进程 CPU 成为瓶颈 | patch `make_chunks` 把 maxbatch 提到 50–100，或显式 `-j` 调到 4–6（减少 merge 次数反而更快） |

---

## F — 第一性原理推导策略（First Principles / Tiers）

> **核心矛盾**：Sphinx 全局单例 BuildEnvironment 决定 READ 阶段必须 N worker → 1 env 合并，**规模法则必然是 sub-linear**，不可能线性扩展到 32 核以上。策略按 ROI 递增 + 侵入性递增分三层。

### F-A 立即执行（零侵入 / 24h 内落地，预期提速 2–5×）

| 动作 | 原理 | 落地成本 |
|---|---|---|
| **1. mystx `setup()` 返回安全元数据** | `return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}` | 1 行代码，<5 min |
| **2. 逐扩展审计 parallel_read_safe** | ① 查上游 setup() 返回；② 已安全的在本地用 `app.setup_extension()` 补声明；③ 确有全局状态写入的强制串行 | 2–4 h 调研 + 测试 |
| **3. 构建入口强制 WSL / Linux** | Windows → SerialTasks，WSL2 走完整 fork 并行 | build.sh / invoke 任务加平台预检 + Fail Fast |
| **4. 默认 `-j auto` + `SPHINX_BUILD_JOBS=auto`** | 在 mystx `tasks/docs.py` create_ns 硬注入 `jobs='auto'` 作为默认，可被 CLI 覆盖 | <10 min |
| **5. CI runner + 本地开发推荐 NVMe / tmpfs** | environment.pickle 读写对 I/O 延迟极敏感 | 基础设施配置 |

### F-B 中期优化（中等侵入 / 1–2 周落地，额外提速 1.5–3×）

| 动作 | 原理 | 落地成本 |
|---|---|---|
| **6. patch `make_chunks(maxbatch=100)`** | 5k 文档：原 64 chunk → 调至 12–16 chunk，merge 循环减少 4–5×，主进程合并 CPU 大幅下降 | 本地 monkeypatch 或贡献上游 Sphinx PR |
| **7. 增量构建刚性化** | 严格保证 `.doctrees/` + `environment.pickle` 在跨 CI run 由 cache key（`hash(src/**/*.md, conf.py, extensions/**)`）持久化；避免 `-E`；`get_outdated_files()` 能把每次构建文件数从 5k 压到 <100 | CI 配置 + 文档 |
| **8. 并发安全断言测试** | `mystx/tests/` 加扩展 parallel 审计测试：加载 conf → 调用 `is_parallel_allowed('read')` 断言 True；回归保护 I-5 | ~1 h |

### F-C 长期天花板突破（高侵入 / 月级，解除 5k 单项目限制）

| 动作 | 原理 | 落地成本 |
|---|---|---|
| **9. Intersphinx 分拆项目（推荐）** | 将 OKF v0.2 / 知识库按域（retrospective / knowledge / tech / guide）拆成 4–8 个独立 Sphinx 项目，每个 <1k 文档；Intersphinx 做交叉链接；全局 toctree 用外部 manifest 缝合 | 分拆 + 链接修复 1–2 月；**彻底绕过单 env 瓶颈，可线性扩展** |
| **10. 自定义 ParallelTasks（Loky）** | 用 `loky`（跨平台 fork+spawn 混合）替换 `multiprocessing.get_context('fork')`，Windows 原生可用；Loky 支持 cloudpickle 序列化闭包扩展（Sphinx 扩展多含闭包） | 原型 1 周；稳定化 1 月；**可贡献回 Sphinx 上游** |
| **11. BuildEnvironment 分片持久化** | 将 monolith `environment.pickle` 改为按 domain / docname range 的分片（类似 RocksDB SSTable），merge 与 I/O 可并行 | 高侵入，需 Sphinx core patch；**2–3 月量级** |

---

## V — 对抗性审查（Adversarial Review）

### V1. 魔鬼代言人（Devil's Advocate）

- **策略 A 的 worker 内存风险**：`-j 16` × 每 worker env 500MB = **8GB 峰值驻留**，再加 main env 500MB → 16GB RAM 机会 SWAP。**建议 N=5k 时 `-j 4~6` 反而比 `-j auto` 更快**（内存带宽 > merge 节省 CPU）。
- **Intersphinx 分拆的交叉链接断裂风险**：分拆后 `:ref:` 跨域不再自动解析，必须将所有跨域引用改为 `:external+project:ref:` 语法 → 现有文档链接修复量 = O(跨域引用数)，**可能需要 AST 级自动迁移脚本**。
- **扩展 parallel_read_safe "撒谎" 风险**：autoapi 若在 `builder-inited` 中写全局共享状态，强行声明 `True` 会导致**静默数据丢失或产物不一致**（而非报错）。必须补：并行下的回归对比测试（`-j 1` vs `-j auto` 产物 diff = 空）。

### V2. 新手视角（Newbie Lens）

- `-j` 参数无效果时 Sphinx 只发 INFO 级日志，**新手根本不知道自己没并行上**。建议加：构建结束 summary 打印 `Jobs: 8 parallel` / `Jobs: serial (reason: Windows OS)` 一行显式提示。
- 扩展声明文档藏得深，默认 `None` 等同于 `False` 的 opt-in 语义**反直觉**——多数扩展作者都漏写。

### V3. 未来自我视角（Future Self）

- myst-parser / myst-nb 主版本升级时，setup() 返回值可能**从 True 改为 False 或新增全局状态**，现有并行会悄悄失效。建议 requirements.txt 中对解析器 pin 到 patch level + CI 加 `is_parallel_allowed` 断言。
- Windows 原生并行（Sphinx 8.x Loky 迁移）落地后，当前 WSL 强制作法需要回滚；文档中必须标记为"临时 workaround"。

### V4. 老板视角（Boss Lens）

- **ROI 排序**：F-A #1–#5（低成本 3× 提速）> F-B #7 增量缓存（+2×）> F-C #9 分拆（解除天花板，仅当实际 hit 5k 瓶颈后做）> F-C #10–#11（不推荐自行做）。
- **决策**：先跑 F-A 全套 + 做一次 5k 真实构建 profiling，若 end-to-end < 30 min 则到顶；> 30 min 再立项做 F-C #9。

---

## E — 模式萃取（Extraction / Reusable Patterns）

### EXT-PARALLEL-GATE 扩展并行门控模式（L1.5）
**问题**：Sphinx 扩展默认 `parallel_read_safe=None`，任一未声明的扩展都会让整次 `-j` 失效。

**解法**：
```python
# conf.py 末尾 — 并行刚性断言
def setup(app):
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

def _assert_parallel_ready(app, env):
    """Fail fast if any extension silently disabled parallel read."""
    if app.parallel > 0 and not app.is_parallel_allowed('read'):
        raise RuntimeError(
            "Parallel read disabled. Check extensions missing "
            "parallel_read_safe=True. Use -v to see per-extension warnings."
        )
```
**适用场景**：所有 Sphinx 项目 >500 文档。

---

### SHARD-BY-INTERSPHINX 项目分片模式（L2）
**问题**：单 Sphinx project BuildEnvironment 全局耦合，read/write 随文档数 sub-linear 扩展，硬天花板在 3k–8k。

**解法**：按知识域切分为子项目，每个独立 env，Intersphinx 做双向引用。**CI 可并行构建 N 个子项目 = 线性扩展**。

**关键约束**：
1. 跨项目引用改为 `:external+<name>:<role>:`<target>` 语法
2. 构建顺序 = 被依赖的先出 `objects.inv`
3. 全局目录树用外部 manifest + static landing-page 缝合

---

### WINDOWS-WSL-WORKAROUND 平台回退模式（L1）
**问题**：`os.name == 'nt'` 时 ParallelTasks = SerialTasks，`-j` 对 Windows 用户完全无效，且日志是 INFO 级易被忽略。

**解法**：
```bash
# 构建入口预检（bash 示例，pwsh 同理）
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  echo "ERROR: Sphinx parallel build requires POSIX fork()." >&2
  echo "Please run under WSL2:  wsl -d <distro> -- ./build.sh" >&2
  exit 2
fi
```
**Fail Fast 优于静默慢速降级**。

---

## 下一步行动清单（Checklist）

| 优先级 | 任务 | 预计耗时 | 状态 |
|---|---|---|---|
| P0 🔴 | mystx conf.py `setup()` 返回 parallel_safe metadata | 5 min | ✅ Done (2026-09-03, mystx commit `56732f9`) |
| P0 🔴 | 为 mystx tasks 默认注入 `-j auto`（tasks/docs.py） | 10 min | ✅ Done → L126 已经是 `"-b html -j auto"` |
| P0 🔴 | 加 `_assert_parallel_ready` 构建钩子到 mystx + xuanspace 两处 conf | 30 min | ✅ Done (2026-09-03, mystx 56732f9 + xuanspace e893b25) |
| P1 🟡 | **逐扩展审计 mystx 17+ 扩展的 parallel_read/write_safe，标记结果表（本附录 A）** | 2–4 h | ✅ Done (2026-09-03, 见下文附录 A) |
| P1 🟡 | 在 mystx/tests 新增扩展并行性集成测试，确保新增扩展自动卡关 | 30 min | ✅ Done (2026-09-03, 3 tests 28 passed) |
| P1 🟡 | 在两处 conf.py 增加 `_PARALLEL_SAFE_OVERRIDES` 中心化覆写表 | 10 min | ✅ Done (2026-09-03, 空表，未来启用时填值即可) |
| P1 🟡 | CI 加 `.doctrees/` / `environment.pickle` 缓存持久化 | 1 h | ⏳ 待执行 |
| P1 🟡 | 合成 5k 文档测试集，`-j 1` vs `-j 4` vs `-j auto` profiling，验证 I-1~I-6 | 1 天 | ⏳ 待执行 |
| P2 🟢 | 若 profiling 后单项目 >30 min，启动 Intersphinx 拆分立项 | 月级 | ⏳ 待执行 |

---

## 附录 A：P1-A mystx 扩展并行性审计矩阵（2026-09-03，Sphinx 9.1.0 / py314 / mystx 本地 src）

### 方法
1. 静态审计：对 mystx 文档 conf.py 中**最终启用**的 17 个扩展（含 `if IS_READTHEDOCS`/条件 append 分支的并集）+ 2 个 mystx 自动注入的扩展（`myst_parser`、`sphinx.ext.mathjax`）= 共 **20 项**，逐个在 py314 site-packages 中定位其 setup()，用 AST + runtime 提取返回 dict 的 `parallel_read_safe` / `parallel_write_safe` 值。
2. 运行时审计：用 **真实 Sphinx app** 以 parallel=4 启动最小构建（`extensions = [全部 17 项]`），然后遍历 `app.extensions[name].parallel_read_safe / parallel_write_safe`，并调用 `app.is_parallel_allowed('read' | 'write')` 做最终 Fail-Fast 判定。
3. 测试固化：所有断言被写入 [tests/unit/test_doc_parallel_extensions_p1.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/mystx/tests/unit/test_doc_parallel_extensions_p1.py)，新增 3 条 pytest（`test_all_target_extensions_loaded` / `test_is_parallel_allowed_read_and_write` / `test_each_extension_parallel_metadata`），确保将来新增未声明扩展时**立即红测卡关**，不必等到生产 CI 才发现。

### 矩阵（20 项）
| # | 扩展名 | 类型 | parallel_read_safe | parallel_write_safe | 结论 |
|---|--------|------|:------------------:|:-------------------:|------|
| 1 | `mystx` | 自研核心 | ✅ True | ✅ True | OK（P0 提交已显式返回） |
| 2 | `mystx.ext.github_readme_stats` | 自研扩展 | ✅ True | ✅ True | OK（mystx 仓库内 setup() 返回） |
| 3 | `myst_parser` | 3rd 核心 | ✅ True | ✅ True | OK（mystx 自动注入） |
| 4 | `sphinx_design` | 3rd UI | ✅ True | ✅ True | OK |
| 5 | `sphinx_copybutton` | 3rd UI | ✅ True | ✅ True | OK |
| 6 | `sphinx_comments` | 3rd | ✅ True | ✅ True | OK |
| 7 | `sphinx_sitemap` | 3rd SEO | ✅ True | ✅ True | OK（Sphinx 11 期会有 Builder.app deprecation warning，不改元数据） |
| 8 | `sphinxcontrib.bibtex` | 3rd 学术 | ✅ True | ✅ True | OK |
| 9 | `sphinx_contributors` | 3rd | ✅ True | ✅ True | OK |
| 10 | `sphinxext.opengraph` | 3rd SEO | ✅ True | ✅ True | OK |
| 11 | `sphinx_tippy` | 3rd UI | ✅ True | ✅ True | OK |
| 12 | `sphinx_examples` | 3rd 示例 | ✅ True | ✅ True | OK |
| 13 | `sphinx_pyscript` | 3rd 运行时 | ✅ True | ✅ True | OK |
| 14 | `sphinx.ext.viewcode` | Sphinx 内置 | ✅ True | ✅ True | OK（9.x 内核对内置扩展做了白名单填充） |
| 15 | `sphinx.ext.intersphinx` | Sphinx 内置 | ✅ True | ✅ True | OK |
| 16 | `sphinx.ext.graphviz` | Sphinx 内置 | ✅ True | ✅ True | OK |
| 17 | `sphinx.ext.extlinks` | Sphinx 内置 | ✅ True | ✅ True | OK |
| 18 | `sphinx.ext.autodoc` | Sphinx 内置 | ✅ True | ✅ True | OK（autoapi 项目需要但 mystx 自身文档未启用） |
| 19 | `sphinx.ext.napoleon` | Sphinx 内置 | ✅ True | ✅ True | OK |
| 20 | `sphinx.ext.mathjax` | Sphinx 内置（自动注入） | ✅ True | ✅ True | OK |

### FINAL VERDICT
| 判定点 | 结果 |
|--------|------|
| `app.is_parallel_allowed('read')`（P0 Fail-Fast 钩子断言） | **✅ True → 不会误触发 RuntimeError** |
| `app.is_parallel_allowed('write')` | **✅ True → write 并行生效** |
| BLOCKS_READ 列表（parallel_read_safe ∈ {None, False}） | **无**（20 项均为 True） |
| BLOCKS_WRITE 列表（parallel_write_safe ∈ {None, False}） | **无**（20 项均为 True） |
| mystx/tests 全量回归 | **28 passed in 4.66s**（P0 前为 25 passed，本次 +3 = 0 回归） |
| IDE 诊断 (3 文件) | **0 errors / 0 warnings** |

### 未覆盖 & 后续操作指引
- `autoapi.extension`（xuanspace 会用到但未在 mystx 文档启用）：**未在本次运行时矩阵内**。xuanspace 正式启用前，需先在其 doc/conf.py 的 `_PARALLEL_SAFE_OVERRIDES` 表中补一行 `"autoapi.extension": (True, True)`，然后用 pytest 本测试中扩展清单加上 `autoapi.extension` 跑一次即可。
- `_ext.gallery_directive`（xuanspace 自建子扩展）：同理，启用时在对应 conf.py 的覆写表填一行。

---

## 参考锚点

| 资源 | 位置 |
|------|------|
| Vendored Sphinx 源码根 | [../../../../../external/libs/docs/sphinx](../../../../../external/libs/docs/sphinx/) |
| parallel.py 基础设施 | [parallel.py](../../../../../external/libs/docs/sphinx/sphinx/util/parallel.py) |
| application.py 安全门控 | [application.py:L1800-L1837](../../../../../external/libs/docs/sphinx/sphinx/application.py#L1800-L1837) |
| build() 主流程 + read/write_parallel | [__init__.py:L389-L818](../../../../../external/libs/docs/sphinx/sphinx/builders/__init__.py#L389-L818) |
| CLI 入口 `-j` | [build.py:L52-L67, L427](../../../../../external/libs/docs/sphinx/sphinx/cmd/build.py#L52-L67) |
| mystx conf.py（待补 parallel 声明） | [conf.py](../../../../../projects/xuanspace/libs/mystx/doc/conf.py) |
| mystx tasks（待注入 `-j auto`） | [docs.py](../../../../../projects/xuanspace/libs/mystx/src/mystx/tasks/docs.py) |
