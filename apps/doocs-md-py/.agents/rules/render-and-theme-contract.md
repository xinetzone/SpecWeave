---
id: "doocs-md-py-rule-render-and-theme-contract"
title: "渲染管线与主题装配契约"
source: "../../AGENTS.md#P0 约束速览"
---

# 渲染管线与主题装配契约

> **适用范围**：修改渲染管线、新增/调整渲染扩展、改主题 CSS 装配、改代码块主题、改渲染验收口径或性能基线。
> **权威事实源**：[../../src/doocs_md_py/render/renderer.py](../../src/doocs_md_py/render/renderer.py)（管线与选项装配的唯一实现）、[../../src/doocs_md_py/render/options.py](../../src/doocs_md_py/render/options.py)（选项默认值）、[../../src/doocs_md_py/render/domcompare.py](../../src/doocs_md_py/render/domcompare.py)（DOM 对拍）、[../../docs/architecture.md](../../docs/architecture.md) §二。

## §1 渲染核心无副作用且三入口共享

- `render/` 是**纯函数式渲染核心**：输入 Markdown 文本 + 选项 → 输出 HTML 片段，**不得产生 I/O 副作用**（不写盘、不打网络、不读环境变量、不依赖进程状态）。
- 三条对外入口（`mdpy` CLI、MCP stdio Server、FastAPI 服务）**共用同一渲染核心**，任何入口的渲染行为差异都是缺陷。**禁止**为某个入口复制一份渲染逻辑。
- 新增渲染能力时，**唯一落点是 `render/`**（必要时 `render/extensions/`），由各入口以相同方式调用。

## §2 管线顺序（不可随意重排）

渲染管线顺序即契约，重排会改变输出；改动顺序必须在 §6 的黄金样例上验证：

1. **front-matter 解析与剥离**（`render/frontmatter.py`）—— 上游 `utils/front-matter.ts` 等价。
2. **markdown-it-py token 遍历 + 17 条渲染规则**（`render/renderer.py`）—— 上游 `renderer-impl.ts` 的 `RendererObject` 逐字复刻。
3. **12 个扩展**（`render/extensions/`，见 §3）—— 装配顺序对齐上游 `extensions/`。
4. **`stripBreakBeforeInlineKatex` 等后处理**（消除行内公式前的换行）。
5. **HTML 净化**（`render/sanitize.py`，后端由 DOMPurify 换 `nh3`，差异 `CD-5`）。
6. **阅读时间 / 脚注 / 风格收尾**（`render/reading_time.py` 等）。
7. **主题 CSS 装配**（`render/css.py`，见 §5）。
8. **外层容器包裹**：输出以 `<section class="container">` 收口（与上游文章结构一致）。

任何步骤的增删都必须在 §6 黄金样例中体现差异，并在 [../../docs/contract-differences.md](../../docs/contract-differences.md) 登记。

## §3 12 个扩展与注册纪律

扩展落点 `render/extensions/`，共 **12 个**（其中 `diagrams.py` 承载 3 个：mermaid / plantuml / infographic）：

| # | 扩展 | 上游锚点 |
|---|------|---------|
| 1 | alert（`alert_data.py` 承载变体数据） | `extensions/alert.ts`（`markedAlert` / `defaultAlertVariant`） |
| 2 | component（`component_data.py` 承载内置组件） | `extensions/component.ts`（`BUILT_IN_COMPONENTS`） |
| 3 | mermaid | `extensions/mermaid.ts` |
| 4 | plantuml | `extensions/plantuml.ts` |
| 5 | infographic | `extensions/infographic.ts` |
| 6 | emoji（`emoji_data.py` 承载 `EMOJI_SHORTCODES`） | `extensions/emoji.ts` / `emoji-data.ts` |
| 7 | footnotes | `extensions/footnotes.ts`（`markedFootnotes`） |
| 8 | katex | `extensions/katex.ts` + `utils/mathDetection.ts` |
| 9 | markup | `extensions/markup.ts`（`markedMarkup`） |
| 10 | ruby | `extensions/ruby.ts`（`markedRuby`） |
| 11 | slider | `extensions/slider.ts`（`markedSlider`） |
| 12 | toc | `extensions/toc.ts`（`markedToc`） |

**注册纪律**：
- 扩展的启用/禁用与注册顺序由 `render/extensions/__init__.py` 集中管理；**禁止**在 `renderer.py` 内部散落注册扩展。
- 数据型模块（`*_data.py`）与逻辑型模块分离：数据由 `scripts/gen-*-data.py` 从上游生成，**禁止手抄大表**（易漂移且不可复核）。
- 新增扩展须：① 上游存在对应 `extensions/*.ts`（否则登记 `CD-` 规格新增）；② 在 `options.py` 增开关且默认值对齐上游；③ 在 §6 黄金样例补样例。

## §4 特色行为不可回退清单

下列行为是 doocs/md 的**标识性特征**，是复刻的核心价值点；**任何情况下不得回退为"通用 Markdown 行为"**（回退等同功能退化）：

| # | 行为 | 说明 |
|---|------|------|
| 1 | 图片尺寸语法 | `![alt\|宽](url)`（仅宽）与 `![alt\|宽x高](url)`（宽×高）解析为带尺寸的图 |
| 2 | `legend` 六值 | 图注 `legend` 选项的六个取值及其渲染差异 |
| 3 | `href === text` 降级 | 链接文本与 URL 相同时渲染为**纯文本**，不输出 `<a>` |
| 4 | `citeStatus` 编号 | 引用态以 `[n]` 编号形式呈现 |
| 5 | `diff-<lang>` 着色 | 代码块语言为 `diff-*` 时按差异高亮渲染 |
| 6 | `data-language-pending` | 待高亮的语言标记属性，供前端后续接管 |
| 7 | Mac 三点窗口装饰 | 代码块顶部的 macOS 风格三点 SVG 装饰 |
| 8 | 代码块行号 | 行号渲染开关与其 DOM 结构 |
| 9 | `hr` 三变体 | 水平线的三种变体渲染 |
| 10 | 列表前缀 | 有序/无序列表的自定义前缀与层级缩进 |

维护要求：上述每条至少一条正向测试断言；改动前先读 `renderer.py` 对应规则，**不得凭"看起来更合理"改结构**。

## §5 主题 CSS 装配与解析

- 主题 CSS 装配与 `var()` / `calc()` 解析的唯一实现是 `render/css.py`（上游 `theme/cssVariables.ts` + `cssProcessor.ts` 逐字复刻，**含上游 `calc()` 已知缺陷的等价复刻**，见 `CD-2`）。
- 解析纪律：
  - 变量替换**有迭代上限**（当前实现 ≤10 轮），新增变量引用不得形成无限间接；
  - 数值取整采用固定精度（当前 round 4 位），**禁止**改用平台默认浮点格式化；
  - `</style` 等序列需转义，避免提前闭合样式块。
- 代码块主题（`render/code_themes.py`）对齐上游 `config-options.ts` 的主题清单；**hljs 主题 CDN URL 白名单**必须与上游一致（数量与串值一致），新增/替换 URL 前先对拍上游常量。
- 主题 CSS 资产位于 `render/assets/*.css`；**禁止**把主题样式硬编码进 Python 逻辑分支。

## §6 验收与黄金样例 / DOM 对拍

- **验收口径 = 归一化 DOM 等价**（NG6），禁止字节比对。裁决工具：[../../src/doocs_md_py/render/domcompare.py](../../src/doocs_md_py/render/domcompare.py)。
- 黄金样例集在 `tests/golden/`：样例输入（如 `complex_doc.md`）与期望输出（`.expected.html`）成对；另有 article 用例与 CSS 快照（`css_snapshot.json`）。
- **再生成纪律**：期望产物由脚本再生成（`scripts/golden_regenerate.py`、`scripts/article_golden_regen.py`、`scripts/css_snapshot_regen.py`）。**禁止手工编辑期望产物**来"让测试变绿" —— 必须先判定差异是否符合上游，符合则按脚本再生成并在 [../../docs/contract-differences.md](../../docs/contract-differences.md) 登记；不符合则为缺陷，修代码。
- 新增渲染能力必须**同时**新增：样例输入、期望输出、以及至少一条聚焦断言。

## §7 性能基线（NFR-6）

- 基准脚本：[../../scripts/bench_render.py](../../scripts/bench_render.py)；复现口径见 [../../docs/coverage-report-t20.md](../../docs/coverage-report-t20.md)。
- 历史基线（仅作参照，**以当次实跑为准**）：100KB 样张渲染 P95 ≈ 355ms（阈值 <500ms）；100 篇同步 P95 ≈ 23ms（阈值 <1000ms）。
- 渲染路径引入新开销（新增扩展、额外正则、二次遍历）前，必须复跑基准；**超阈值即缺陷**，不得调高阈值掩盖。

## §8 反模式（出现即打回）

| # | 反模式 | 后果 |
|---|--------|------|
| A1 | 在 `render/` 内做文件读盘、网络请求或读取环境变量 | 破坏无副作用契约，三入口行为分裂 |
| A2 | 为单一入口复制渲染逻辑 | 三入口行为漂移 |
| A3 | 手改 `.expected.html` 使测试变绿 | 掩盖真实差异，黄金样例失效 |
| A4 | 把特色行为（§4）"简化"为通用 Markdown 行为 | 功能退化，复刻价值丧失 |
| A5 | 手抄 emoji/alert/component 大表而非用 `gen-*-data.py` | 数据漂移不可复核 |
| A6 | 在验收标准中写字节比对 | 违反 NG6 |
| A7 | 随意重排管线顺序或调整扩展注册顺序 | 输出改变但无差异登记 |

## 变更纪律

- 本文档只增不删；管线顺序、扩展清单、验收口径、性能阈值四者变更均须先更新 [../../docs/architecture.md](../../docs/architecture.md) §二 与黄金样例，再回写本文，最后记 [../CHANGELOG.md](../CHANGELOG.md)。
