# KaTeX 官网学习与 OKF Wiki 更新 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: R 阶段——采集官网事实并更新事实清单
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 系统读取官网 17 个公开页面：首页、Users、Versions、Node、Browser、API、CLI、Auto-render、Extensions & Libraries、Options、Security、Handling Errors、Font、Supported Functions、Support Table、Common Issues、Migration。
  - 在 `spec/facts.md` 中追加官网事实，建议使用 `W-xxx` 编号；保留现有源码事实，发现冲突时新增“事实复核/修正”小节，不得静默覆盖。
  - 重点复核 Options 默认值、CLI 参数、Browser/Node 安装方式、Auto-render 选项、Security 策略、Font/Sass/Browserslist、Supported Functions、Migration 变更。
  - 所有事实必须包含来源 URL 或源码路径，R 阶段只记录“页面/源码中有什么”，不写推断。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-11
- **Test Requirements**:
  - `programmatic` TR-1.1: `spec/facts.md` 中至少出现 17 个官网页面路径（`https://katex.org/...`），每页至少 3 条事实。
  - `programmatic` TR-1.2: 对 `strict`、`maxExpand`、`throwOnError`、`errorColor`、`trust`、`globalGroup` 的默认值给出官网来源；若与现有事实不同，必须有修正记录。
  - `human-judgement` TR-1.3: 抽查事实条目，不应出现“用于、目的是、设计为、显然、因此”等推断词；解释性内容应移入 I 阶段或正文。
- **Notes**: 官网事实与源码事实冲突时，在事实清单中并列记录来源和结论，再由后续文档任务采用复核后的表述。

## [x] Task 2: I 阶段——更新洞察与知识地图
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 更新 `spec/insights.md`，围绕官网文档与源码架构的关系提炼 3-5 个洞察四元组。
  - 输出完整文档地图：现有文档更新点、新增文档列表、每个官网页面映射到的文档。
  - 明确学习路径：使用 KaTeX、理解架构、扩展开发、升级排障。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每个洞察均包含陈述、证据、反常识/差异、行动四部分。
  - `programmatic` TR-2.2: 知识地图列出 00-23 全部概念文档、5 个现有示例、3 个新增示例和 references 文件。
  - `programmatic` TR-2.3: 17 个官网页面均在映射表中出现一次以上。
- **Notes**: 不重写已有源码洞察；重点补充“官网用户视角”和“事实偏差修正”洞察。

## [x] Task 3: E 阶段——先建立 references 信源基线
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 新增 `references/katex-website.md`，登记官网 17 个页面的 ID、URL、标题、页面用途和引用提示。
  - 更新 `references/katex-source.md`，在必要处补充 v0.18.4 源码路径和官网关联说明。
  - 确保后续所有文档的 `sources.resource` 都能指向本任务生成的 reference 或外部 URL。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: `references/katex-website.md` 存在，包含 17 个页面条目和稳定 ID（如 `web-options`、`web-cli`）。
  - `programmatic` TR-3.2: 两个 reference 文件均有合法 YAML frontmatter 和非空 `type: Reference`。
  - `human-judgement` TR-3.3: 官网页面标题、URL 和用途与盘点结果一致。
- **Notes**: 遵循信源先行纪律；此任务完成前不生成 concepts/examples 内容。

## [x] Task 4: E 批次 1——入门、API、运行时与 CLI
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 更新 `concepts/00-introduction.md`：融合首页卖点、Users/Versions 入口、版本与许可信息。
  - 更新 `concepts/01-getting-started.md`：融合 Browser、Node、API 页面，修正 CDN、核心 API、String.raw、错误处理、持久宏说明。
  - 更新 `concepts/10-settings-options.md`：以官网 Options 页面为准修正配置表和默认值，补充 trust context、macro 函数、MacroExpansion、globalGroup。
  - 新增 `concepts/15-installation-and-runtime.md`：系统说明浏览器 CDN/自托管、Node/npm/pnpm/yarn/Deno、ESM/CJS、CSS/字体路径、Bundler、Browserslist/USE_FONT 构建说明。
  - 新增 `concepts/16-command-line.md`：说明 CLI 输入/输出、17 个参数、与 Options 的映射、宏文件和常见用法。
- **Acceptance Criteria Addressed**: AC-5, AC-11
- **Test Requirements**:
  - `programmatic` TR-4.1: 5 个文档均存在、有 frontmatter、`sources` 至少引用官网 reference 或源码 reference。
  - `programmatic` TR-4.2: Options 表中 `strict`、`maxExpand`、`minRuleThickness`、`globalGroup` 等默认值与官网事实一致。
  - `programmatic` TR-4.3: CLI 文档覆盖官网列出的全部 18 个选项（含 `--version` 与 `--help`）。
  - `human-judgement` TR-4.4: 入门路径从安装到首次渲染连贯，代码片段可复制，选项说明没有遗漏关键安全警告。
- **Notes**: 本批共 5 个文件，符合每批 ≤7 要求。

## [x] Task 5: E 批次 2——扩展、字体、样式、安全与错误
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 更新 `concepts/11-style-system.md`：补充官网 Font 页面中与样式、字号、单位相关的用户视角说明。
  - 更新 `concepts/12-font-metrics.md`：融合 Font 页面，补充字体格式、Browserslist、Sass 变量、字体目录和 1.21em 默认缩放。
  - 更新 `concepts/13-auto-render.md`：以官网 Auto-render 页面为准修正 delimiters 默认值、ignoredTags、preProcess、errorCallback、displayMode 行为和宏持久化。
  - 更新 `concepts/14-contrib-extensions.md`：聚焦官方扩展 auto-render、copy-tex、mathtex-script-type、mhchem、render-a11y-string；第三方库索引移至生态文档。
  - 新增 `concepts/17-fonts-and-units.md`：面向使用者说明字体加载策略、`katex-swap.css`、单位换算、绝对长度缩放、字体自托管。
  - 新增 `concepts/18-security-and-errors.md`：融合 Security 与 Handling Errors，说明 trust、maxSize、maxExpand、HTML 消毒、ParseError、错误消息转义。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 6 个文档均存在且 `sources` 覆盖 Font、Security、Error、Auto-render、Libs 等官网页面。
  - `programmatic` TR-5.2: Auto-render 默认 ignoredTags 列表与官网事实一致；displayMode 由 delimiter.display 决定的说明存在。
  - `human-judgement` TR-5.3: 安全文档明确列出 trust 控制的 HTML/URL/资源命令和消毒白名单风险。
  - `human-judgement` TR-5.4: 字体文档能解释 CSS、字体目录和 Sass/Browserslist 之间的关系。
- **Notes**: 本批共 6 个文件；源码架构解释与官网用户文档应明确分层，不互相替换。

## [x] Task 6: E 批次 3——支持函数、支持表、问题、迁移与生态
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 新增 `concepts/19-supported-functions.md`：按官网分类整理 Accents、Delimiters、Environments、HTML、Layout、Logic、Macros、Operators、Relations、Style/Color/Size/Font、Symbols、Units 等。
  - 新增 `concepts/20-support-table.md`：说明字母序支持表的用途、支持/不支持条目的阅读方式、Detexify 和源码/宏定义溯源。
  - 新增 `concepts/21-common-issues.md`：覆盖 DOCTYPE、智能引号、aligned/matrix 间距、align vs aligned、color 差异、MathJax 命名差异、CSS 排障。
  - 新增 `concepts/22-migration.md`：整理 v0.13-v0.18 迁移要点，尤其是 CSS 类名前缀、`__defineFunction`、contrib 路径、`\relax`、宏参数行为。
  - 新增 `concepts/23-ecosystem-and-versions.md`：覆盖 Users、Versions、官方扩展入口和第三方库索引（React/Vue/Angular/Android/iOS/Rust/Ruby/小程序等）。
  - 更新 `examples/basic-render.md` 与 `examples/error-handling.md`，使其与官网 API/Error/Security 表述一致。
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: 5 个新概念文档均存在，且覆盖 Supported、Support Table、Issues、Migration、Users/Versions/Libs 页面。
  - `programmatic` TR-6.2: 19-supported-functions 包含官网 14 个 H2 分类名称。
  - `programmatic` TR-6.3: 22-migration 覆盖 v0.13、v0.14、v0.15、v0.16、v0.17、v0.18 六个版本段。
  - `human-judgement` TR-6.4: 两个示例中的错误处理和安全提示可直接指导使用者规避 XSS 与不可信输入风险。
- **Notes**: 本批共 7 个文件，达到批量上限；不要额外夹带其他文件。

## [x] Task 7: E 批次 4——宏、扩展示例与 Node 安全示例
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 更新 `examples/custom-macros.md`：补充共享 `macros` 对象、`\gdef` 持久化、宏安全边界、函数型宏和 MacroExpansion 概念。
  - 更新 `examples/custom-extension.md`：对照官网/源码事实检查 `__defineFunction`、builder、MathML 无障碍要求。
  - 新增 `examples/node-ssr.md`：展示 Node.js/ESM/CJS 中 `renderToString`、CSS 引入、HTML 注入注意事项。
  - 新增 `examples/security-trust.md`：展示不可信输入配置、trust 函数、错误处理、HTML 消毒和持久宏隔离。
- **Acceptance Criteria Addressed**: AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1: 4 个示例文档均存在且包含语言标注代码块。
  - `programmatic` TR-7.2: custom-macros 示例中 `macros` 对象在多次 `render`/`renderToString` 调用间共享。
  - `human-judgement` TR-7.3: security-trust 示例清楚说明何时可启用 trust、何时必须消毒输出。
- **Notes**: 本批共 4 个文件；示例不要求实际运行工程，但 API 名称和选项必须可溯源。

## [x] Task 8: E 批次 5——Auto-render 与 CLI 示例
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 更新 `examples/auto-render-usage.md`：补充默认 delimiters、ignoredTags、ignoredClasses、preProcess、errorCallback、动态内容和宏持久化。
  - 新增 `examples/cli-render.md`：展示 `npx katex` 从 stdin 到 stdout、文件输入输出、display mode、宏文件、错误处理等命令。
- **Acceptance Criteria Addressed**: AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 两个示例文档均存在，CLI 示例覆盖 `--input`、`--output`、`--display-mode`、`--macro`、`--macro-file`、`--no-throw-on-error`。
  - `human-judgement` TR-8.2: Auto-render 示例能解释 delimiter 顺序和 `$$` 先于 `$` 的原因。
- **Notes**: 本批共 2 个文件。

## [x] Task 9: E 收尾——索引、导航与更新日志
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 更新根 `index.md`：补齐 15-23 新概念文档、8 个示例、官网学习路径、核心洞察和版本信息；在根 frontmatter 中声明 `okf_version: "0.2"`。
  - 新增 `concepts/index.md`、`examples/index.md`、`references/index.md`，子目录 index 不写 frontmatter。
  - 新增或更新 `log.md`，记录 2026-08-23 本次官网学习与融合增强。
- **Acceptance Criteria Addressed**: AC-1, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 根 `index.md` 列出的所有概念和示例文件均存在。
  - `programmatic` TR-9.2: 三个子目录 `index.md` 均存在且无 YAML frontmatter。
  - `programmatic` TR-9.3: `log.md` 存在且包含日期 `2026-08-23`。
  - `human-judgement` TR-9.4: 学习路径能区分使用、架构、扩展、排障/迁移四类读者。
- **Notes**: Index 必须最后写，避免新增文件后遗漏导航。

## [x] Task 10: V 阶段——独立验证与修复闭环
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 委派独立验证子智能体检查官网覆盖、frontmatter、链接、信源、代码示例、事实一致性。
  - 对发现的问题进行最小修复；修复后重新验证。
  - 更新任务清单和检查清单状态，输出验证摘要。
- **Acceptance Criteria Addressed**: AC-9, AC-10, AC-12
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有非保留 Markdown 文档均有可解析 YAML frontmatter 和非空 `type`。
  - `programmatic` TR-10.2: 所有 bundle 内 `/` 开头链接目标存在；无 `file:///` 链接进入产物文档。
  - `programmatic` TR-10.3: 检查 17 个官网 URL 均被 reference 或文档 sources 覆盖。
  - `programmatic` TR-10.4: 文档中不得出现已确认错误的默认值（如未修正的 `strict: false`、`maxExpand: 1000` 作为官网默认值）。
  - `human-judgement` TR-10.5: 随机抽查 5 篇新增/更新文档，事实表述均可追溯到 facts.md 或 references，无明显虚构 API。
- **Notes**: 验证子智能体不得只做结构检查，必须核对官网事实和示例 API。
