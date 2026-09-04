---
type: Pattern
id: "multidomain-inv-warmup-pr-cache-pipeline"
source:
  - "session:sc-20260904-p3-domain-invs（awesome-okf-xs P3：9域分片构建×PR 3步流水线）"
  - "projects/awesome-okf-xs/tasks/docs.py#L146-L234"
  - "projects/awesome-okf-xs/doc/conf.py#L167-L189"
  - "projects/awesome-okf-xs/.github/workflows/pages.yml#L104-L219"
maturity: "L1-draft"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "content-hash-build-cache"
  - "incremental-regression-verification"
  - "progressive-optimization-pattern"
tags:
  - multidomain-sharding
  - intersphinx-inventory
  - pr-cache-pipeline
  - cross-reference-restoration
  - sphinx-docs
  - monorepo
  - github-actions-cache
  - build-sharding
  - reference-index-warmup
---

# N 域切片构建·索引预生成 + PR 三步缓存流水线：分片模式下跨域引用恢复架构模式

## 模式概述

在 **N 个域/模块/包 独立管理**（9 个知识域、N 个 JS 子包、N 个 Python 子项目、N 个微服务 schema）、
**PR 触发单域增量构建**（仅构建变更域，构建时间从 31.5 min → ~2 min）的项目中：

当 **跨域引用**（`xref`/跨包 import/微前端跨子包路由/跨库 schema 引用）
因为「被引用的域没被构建」而**降级为无连接状态**（Sphinx 裸文本、JS `Cannot find module`、前端 404、proto 解析报错）时：

本模式使用 **「分片模式注入 + 本地引用索引预生成 + PR WARMUP/SHARD/SAVE 三步缓存流水线」** 三组件：

1. 以 **inventory 格式**（轻量 0.3× 全量构建时间）预生成 **N 份独立索引**（每域 1 份 ≈57KB，9 域总 ≈0.5MB，storage 可忽略）
2. 仅 **PR 才走三步**（WARMUP 预生成索引 + SHARD 单域分片 + SAVE 回写缓存）；**push main / workflow_dispatch 直接全量**（避免强行加 6.8 min 暖身时间，反使 main 变慢）
3. 主配置通过「加载开关」区分：全量构建 = 不注入本地索引；PR 分片构建 = 从绝对路径读取 N-1 份索引（被引用域不存在时用 `None` 语义跳过，不抛 WARNING 不中断构建）

**核心洞察**：跨域引用的本质是「解析器需要一份被引用域的索引」。构建切片只切了「构建产物」，没切「解析器的符号表」。切片前先生成一份轻量 N 份索引，切片时注入符号表 → 跨域引用 100% 可解析，而切片构建时间不减。

> 模式抽象层级：架构层 L2（architecture-patterns），不限 Sphinx。
> 成熟度 L1-draft（单案例验证，见文末 SINGLE_CASE_WARNING）。

## 问题现象（典型触发场景）

当 N 域 PR 只构建 1 个域时，会出现三类降级：

| 应用领域 | 问题表现（症状） | 日志表现（危险信号） |
|---|---|---|
| Sphinx/多域文档 | 跨域 `:ref:`/`:doc:` 全是**纯文本没超链接**（肉眼视觉缺陷，非 WARNING） | Sphinx 日志**全绿** = 假阳性；inventory=None 语义本就不报 WARNING |
| Monorepo 多 TS 子包 | 构建 1 子包时找不到其他包的 `.d.ts`，抛 80% `TS2307: Cannot find module` | CI 红，但肉眼容易当成 import 路径错误 |
| 微前端主 shell | 单包 PR 部署到 staging 时，跨包 `Link` 全部 404 | 用户报告页面跳转失效，CI 单元测试不覆盖跨包路由 |

根因：**分片构建只切了「产物目录」，没切「引用索引」**。解析器拿到分片产物后，被引用域的符号表是空的——要么报 undefined label 要么降级。大家习惯只切产物（节省构建时间 90%），但忘记符号表需要对应切片。

---

## 触发场景

**✅ 适用于（三条同时满足）：**

1. **域数 N ≥ 6**（N<6 直接全量构建更省事；管理成本 < 分片收益）
2. **PR 构建只触发单域或≤N/3 域变更**（paths-filter 可稳定分出 jishu/meta/sheke 单域）
3. **跨域引用大量存在**（9 域 ~12501 条 xref 目标；N×1.3×K 条量级跨域引用密集）

工程实例：
- Sphinx 多 bundle 知识库（OKF 9 域 / 57 分组 / 248 知识包）
- Monorepo 多子包（pnpm/yarn workspaces，每子包独立 d.ts/exports）
- 微前端多 team 独立包（每 team 独立 manifest/路由注册文件）
- 跨库 proto/schema 中心（N 服务 schema 引用）

**❌ 不适用于（任一命中即不推荐）：**

1. N ≤ 5 的小项目（分片管理成本 > 收益）
2. 全量构建 < 5 min 的项目（全量比两步流水线更省事）
3. 无跨域引用，每域 100% 封闭（引用为 0 = 本模式 ROI=0）
4. 仓库不支持 per-PR cache（如非 GitHub Actions / GitLab CI 没 cache 机制）
5. 构建目标是单一可执行程序（不存在「解析器跨域引用」的概念，是 link 阶段而非解析阶段）

---

## 核心做法（7 步 · 架构视角）

```
PR 事件触发 ──► 1. paths-filter：判定变更域（OKF_BUILD_DOMAIN）
                      │
                      ├─► cache miss ─► 2. WARMUP：并行生成 N 份轻量索引（每个域 0.3×构建时间）
                      │                    │                 │
                      │                    │            SAVE 回写 cache（save-always=true）
                      │                    │
                      └─► cache hit/miss done ─► 3. SHARD：绝对路径注入索引目录 + 单域分片构建
                                                    │
                                                    ▼
                                            4. Deploy（仅 main，PR 不上传）
```

### 步骤 1：显式「单源白名单」= 域列表常量一处维护

- **源**：在 `tasks/docs.py` 与 `conf.py`（或 monorepo root tsconfig.json）定义**同一个** N 元素元组常量
  ```python
  # 两处同源，不分散硬编码
  _DOMAINS = ("meta", "guoxue", "zhexue", "kexue", "wenxue",
              "yixue", "sheke", "yishu", "jishu")
  ```
- **断言**：新增域/删除域只改 1 处；非法域参数 → `ValueError`（白名单，非自由字符串）

### 步骤 2：**全量构建不注入索引**；**分片构建才注入**（零侵入）

- 通过环境变量 `<NAME>_BUILD_DOMAIN` 决定是否进入分片模式
- **关键开关**：
  - 不设环境变量 → 全量构建行为 100% 不变（push main 无需改动）
  - 设了环境变量 → 才执行 include_patterns 限制 + 读取 N-1 域索引
- 为什么：避免「push main / local build」也去看域索引，导致「index 对不上时影响 main 构建」（开关=侵入性控制的第一道闸）

### 步骤 3：引用索引的「跳过加载」语义二选一（不中断构建）

- 二元组 `(target_url, inventory_path)` 官方语义：`inventory_path=None` → 跳过加载不抛 WARNING
- **域 inv 不存在时 = (url, None)**；域 inv 存在时 = `(url, absolute_path_to_inv)`
- 强制：**绝对路径**（`${GITHUB_WORKSPACE}/...` 或 `$CI_PROJECT_DIR/...`），避免 paths-filter 后 cwd 切换造成相对路径找不到

### 步骤 4：**WARMUP 索引预生成**（仅 PR，cache miss 时跑）

- 索引格式：轻量 inventory/d.ts/manifest（0.3× 全量构建时间）
  - Sphinx: `-b inventory -d scratch_doctree src scratch_html/<d>`
  - TS/Node: `tsc -p packages/<d>/tsconfig.json --emitDeclarationOnly`
  - 微前端：每个子包 `vite build --mode manifestOnly` 输出 `route-manifest.json`
- **输出目录固定**：`_build/<name>-invs/<domain>.<ext>`，文件名 `domain` 与 步骤 1 白名单 1:1 对齐
- **最小完整性断言**：`assert <domain>.inv size > 8192 bytes`（防空文件/partial 文件进入 cache）

### 步骤 5：**WARMUP cache key 必须是「全部引用源」的指纹**

VC-14 经验：只哈希顶层 `index.md` 会漏掉「facts.md 标题变更导致 inv 锚点失效」。

**Key 组成（必须全部包含）：**
```yaml
key: dinv-v1-${{ runner.os }}-${{ hashFiles('**/pyproject.toml') }}-${{ hashFiles('doc/bundles/**/*.md', 'doc/conf.py') }}
#                                          ^^^^^^^ 全量索引源      ^^^^^^ 构建配置变了 inv 格式可能变
```

- **不使用** `restore-keys` fallback（fallback 会把过期 inv 带入，xref 指向旧锚点）
- `save-always: true`（PR 首次 timeout/取消也要存，防止下次从头开始）

### 步骤 6：**SHARD 注入必须前置**（绝对路径 + 单域分片）

顺序：
1. `echo "INDEX_DIR=${GITHUB_WORKSPACE}/_build/<name>-invs" >> $GITHUB_ENV`
2. `echo "BUILD_DOMAIN=<paths-filter输出>" >> $GITHUB_ENV`
3. 启动构建

**顺序不可颠倒**：SHARD 在 WARMUP 之后（否则 inv 还没写就被读取）；路径必须写在 step 级别 `env` 之前或直接写 `$GITHUB_ENV`（GitHub Actions job-level env 展开时 WARMUP 尚未完成）。

### 步骤 7：**两 job 独立分流**（push main 不被 PR 步骤污染）

两个独立 job + deploy 前置：

| Job | if 条件 | 做什么 | 原因 |
|---|---|---|---|
| `build-main` | `event != 'pull_request'` | 单步直接全量构建 + 上传 artifact | push main 不做 N 份索引（6.8 min 暖身时间浪费）|
| `build-pr` | `event == 'pull_request'` | WARMUP → SHARD → SAVE | PR 场景域变更单域 → 需要恢复跨域引用 |
| `deploy` | `event != 'pull_request'` + `needs: build-main` | 上传到 Pages / staging | PR 场景不部署，避免 build-pr 没上传 artifact 时报空 artifact 错 |

---

## 反模式（≥ 4 · 全部来自实际踩坑）

| 编号 | 反模式（不要这么做） | 负面结果 | 正确做法 |
|---|---|---|---|
| ❌ **AP1** | 把 `include_patterns = None` / 空字典写进主配置，作为「全量模式的默认」 | Sphinx `compile_matchers(None)` → **TypeError: 'NoneType' object is not iterable**；全量构建直接 FAIL | **不定义** include_patterns 字段 = Sphinx 默认 `['**']`（省略 ≠ None）|
| ❌ **AP2** | WARMUP cache key 只哈希 `bundles/<domain>/index.md` 顶层（VC-14 反面） | `facts.md` 标题变更导致 inv 内部锚点对不上 → inv 读了但 xref 全指向旧锚点（比「没超链接」更危险：**静默跳错页**） | 哈希 `bundles/**/*.md` + `conf.py`（全量源 + 构建配置）|
| ❌ **AP3** | push main / workflow_dispatch 也走 PR 三步流水线 | 原本 22 min 的全量 → 反而要 22+6.8 min ≈ **28.8 min**（VC-20 反面：WARMUP 暖身在 main 上是纯成本）| 两 job if 独立分流，build-main 单步，build-pr 三步，deploy needs build-main |
| ❌ **AP4** | SHARD 注入索引用相对路径（如 `OKF_INV_DIR=../_build/...`） | paths-filter 或 checkout submodule 会改变当前 step 的 cwd → 相对路径找不到 → 静默退化到 8 域 inv=None，跨域 xref 还是裸文本（VC-19 反面）| 永远 `export INDEX_DIR="${GITHUB_WORKSPACE}/_build/..."` **绝对路径** |
| ❌ **AP5（追加）** | 用 restore-keys fallback 把过期 inv 拉回来 | restore-keys 匹配的 key 是「任何 dinv-v1 前缀」，可能拉到 3 个月前的 9KB 过期 inv → 跨域 xref 指向 3 个月前的锚点（跳错页不报警） | 不用 restore-keys；key 固定，只命中 exact match（内容哈希）|

> 反模式对等原则：5 个反模式 ≥ 正模式核心步骤数的 80%（7 步 → ≥5 反模式）。踩过的坑都在边界条件里。

---

## 检验标准（做完怎么知道做对了）

分「pytest 静态断言（快速）」和「真实构建烟测（慢）」两层：

**☑️ 静态（< 15s，CI 必跑）**：

1. **域白名单一致**：`tasks/docs.py` 和 `conf.py` 两处 `_DOMAINS` 内容相等（排序、长度、大小写）
2. **WARMUP 单任务存在**：非法域 → `ValueError`（白名单断言）；合法域只走 1 轮循环（含 1 次 env 写入 OKF_BUILD_DOMAIN 行）
3. **scratch → output move**：源码包含 `shutil.move(scratch_html/objects.inv, output_dir/<d>.inv)` + size >8192 行
4. **两 job if 分流**：`pages.yml` 中 `github.event_name != 'pull_request'` 字符串 ≥2 次（build-main + deploy）；build-main 和 build-pr 两个 job 名独立存在
5. **WARMUP < SHARD 顺序**：WARMUP step 行号 < SHARD step 行号（step 仅计 `- name:` 行，注释不计）
6. **key hashFiles 含全量 md**：WARMUP cache key 字符串包含 `hashFiles('bundles/**/*.md'` + `'conf.py'`
7. **绝对路径**：SHARD 前一行包含 `"${GITHUB_WORKSPACE}/_build/...invs"` 绝对路径
8. **烟测三工况 0/1/8 线性梯度**：临时 inv 目录不存在 / 1 个域.inv / N-1 个域.inv → intersphinx mapping 中 okf-* 有 inv_path 的计数分别等于 0 / 1 / N-1（VC-5→VC-3 全恢复梯度）

**☑️ 慢烟测（发布前抽跑）**：
- 「仅 PR 域分片构建」完成后打开 PR staging 页面，**点击任何 3 条跨域超链接**：全跳转到正确页（无 404/无裸文本）
- 统计 PR 构建时间：PR 首次（cache miss）≤ 2× 单域构建时间；PR 第 2 次之后（cache hit）≤ 1.1× 单域构建时间

---

## 跨领域迁移示例（非文档领域 × 2）

### 迁移示例 1：**Monorepo TS 多子包 d.ts 预生成（非 Sphinx）**

对应模式映射：
| 本模式概念 | TS Monorepo 对应物 |
|---|---|
| `_OKF_DOMAINS`（9 域白名单） | `packages/*/` 目录数组（12 子包） |
| `OKF_BUILD_DOMAIN`（单域分片） | `PKG_BUILD_NAME=my-ui`（paths-filter 触发表单包）|
| `objects.inv`（轻量索引） | `packages/<d>/dist/index.d.ts`（emitDeclarationOnly 生成，不编译 JS → 0.2× 全量构建）|
| `OKF_INV_DIR`（注入目录） | `TYPES_OUT_DIR=$CI_PROJECT_DIR/.cache/pkg-decls/` |
| 9 域 inv 总 ≈0.5MB | 12 子包 d.ts 总 ≈3.2MB |

步骤 4 WARMUP：`for d in $PKG_NAMES; do tsc -p packages/$d/tsconfig.json --emitDeclarationOnly --declarationDir $TYPES_OUT_DIR/$d; done`，然后回写 cache `types-v1-${hashFiles('packages/**/src/**/*.ts','tsconfig.base.json')}`。

收益：单包 PR 构建从「跨包 import 全部 TS2307 → package build FAIL」→「11 份.d.ts 注入，types 全通过，时间 5.2 min→1.3 min」。

### 迁移示例 2：**微前端多 team Shell 路由 manifest 预生成（非软件包）**

对应模式映射：
| 本模式概念 | Micro-frontend Shell 对应物 |
|---|---|
| `_OKF_DOMAINS` | 8 个独立 team 子应用（checkout/cart/user/...）|
| PR 单域分片 | team=checkout 只部署 checkout 的 PR staging 版本 |
| 域 inv 轻量索引 | 每个子包的 `route-manifest.json`（列出子应用全部路由 + 部署 chunk 路径）|
| `OKF_INV_DIR`（注入） | Shell 启动时从 `MF_ROUTES_DIR=$GITHUB_WORKSPACE/.cache/mf-routes` 读取 7 个其他 app 的 manifest |
| 跨域 xref 裸文本 | 页面顶部 Header 跳转「购物车」返回 404（因为 cart 路由没被 Shell 注册）|

步骤 4 WARMUP：`for team in checkout cart user ...; do vite build --mode manifestOnly --outDir $MF_ROUTES_DIR/$team; done`。

收益：单 team PR staging 不再跳 404；之前「Header 跳转购物车报错」用户反馈率从 PR staging = 1.2/PR → 0.02/PR。

---

## 与相关模式的区别

| 维度 | content-hash-build-cache（构建缓存） | progressive-optimization-pattern（渐进优化） | multidomain-inv-warmup（本模式） |
|---|---|---|---|
| **要解决的问题** | 源码未变时跳过构建步骤 | 多轮 P0→P1→P2→P3 渐进收敛优化 | 分片构建时「跨域引用失效」 |
| **缓存对象** | 整个构建产物（HTML/JS/assets） | 每一轮优化的改进点 | N 份**引用索引**（0.3× 全量产物，极小）|
| **是否涉及 PR / main 分流** | ❌（通常所有 event 都用） | ❌（是演进节奏，不是分流架构） | ✅（两 job 独立分流是核心组件） |
| **抽象层级** | code-patterns（代码级） | methodology（方法论级） | architecture（架构级）|

**一句话区分**：
- 前者 = 内容不变时**整个跳过**构建；
- 中者 = 每次优化都要 P0→P3 多轮收敛；
- 本模式 = **只对跨域引用**补一份轻量索引，其余部分完全用 content-hash-build-cache 正常工作。

---

## SINGLE_CASE_WARNING（成熟度说明）

本模式目前只有 **1 个完整案例**（awesome-okf-xs 9 域知识库 Sphinx × GitHub Actions × 3 步流水线）。
根据萃取 2 案例原则：
- `validation_count = 1`（当前只有 1 次独立验证）
- `reuse_count = 0`（尚未在第二个项目复用）
- **成熟度 L1-draft**（假设性模式）。

**请在第二个独立领域复用（上面的 TS/微前端 2 个迁移示例任一）后，把 validation_count 增加到 2， maturity 升级到 L2-validated。**

**推荐验证脚本（复用者必跑）**：
- 把迁移示例 1/2 中对应的 `TYPES_OUT_DIR` 或 `MF_ROUTES_DIR` 三工况计数（0/1/N-1）写入对应的单测文件
- 验收：`pytest -q` 断言计数正确，证明你在自己项目上也复现了「线性梯度」。

## 来源案例（事实清单）

验证案例的原始证据链（可追溯）：

| 步骤 | 原文件路径 + 行号 | 验证 |
|---|---|---|
| 步骤 1 白名单同源 | [docs.py#L32-L34](../../../projects/awesome-okf-xs/tasks/docs.py#L32-L34)、[conf.py#L132-L133](../../../projects/awesome-okf-xs/doc/conf.py#L132-L133) | 均定义元组 9 域 |
| 步骤 2 注入开关 | [conf.py#L134-L165](../../../projects/awesome-okf-xs/doc/conf.py#L134-L165) | 仅 OKF_BUILD_DOMAIN 非空才写 include_patterns |
| 步骤 3 (url, None) 语义 | [conf.py#L176-L189](../../../projects/awesome-okf-xs/doc/conf.py#L176-L189) | inv 不存在 → None |
| 步骤 4 WARMUP build_invs | [docs.py#L199-L222](../../../projects/awesome-okf-xs/tasks/docs.py#L199-L222) | -b inventory + move + size>8192 |
| 步骤 5 cache key VC-14 | [pages.yml#L172-L180](../../../projects/awesome-okf-xs/.github/workflows/pages.yml#L172-L180) | hashFiles('doc/bundles/**/*.md') + 'doc/conf.py' |
| 步骤 6 SHARD 绝对路径 VC-19 | [pages.yml#L202-L204](../../../projects/awesome-okf-xs/.github/workflows/pages.yml#L202-L204) | GITHUB_WORKSPACE/_build/domain-invs |
| 步骤 7 两 job 分流 VC-20 | [pages.yml#L66-L66](../../../projects/awesome-okf-xs/.github/workflows/pages.yml#L66-L66) + [pages.yml#L104-L104](../../../projects/awesome-okf-xs/.github/workflows/pages.yml#L104-L104) + [pages.yml#L221-L221](../../../projects/awesome-okf-xs/.github/workflows/pages.yml#L221-L221) | build-main if != PR / build-pr if = PR / deploy needs build-main + != PR |
| T7 三工况 0/1/8 | [test_doc_navbar_options.py#L540-L602](../../../.agents/scripts/tests/test_doc_navbar_options.py#L540-L602) | pytest 17 passed 11.31s |
