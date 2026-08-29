# Prompt 模板集

> 各阶段执行时复制对应Prompt，替换`<占位符>`后使用。

## 阶段0：信源稳定性预检（R阶段前必做，G0）

```
在开始源码学习之前，先执行信源稳定性预检（信源稳定性门）：

1. 信源分类：列出本次全部信源（源码仓库/克隆/下载包），按路径特征段分类：
   - temporary：.chaos/、.tmp/、系统 Temp、缓存目录中的临时克隆
   - stable：vendor/ 子模块、site-packages、系统安装目录
   - env-bound：开发者机器任意绝对路径（Desktop、home 等）
2. 临时信源升级：temporary/env-bound 信源必须先固定为可追溯副本：
   - 首选 git submodule 固定到具体 release tag，记录 tag 名 + commit hash + 远程 URL
   - 次选固定到具体 commit hash
   - 禁止固定 main/master/浮动分支（分支会前进 = 信源漂移）
   - tag 选型判据：文档引用集合 ∩ 版本变更集合 = ∅（引用的 API 在所选版本中全部存在）
3. 路径纪律：facts.md 与后续文档中的信源路径只指向 stable 位置（vendor/<lib>），
   禁止 file:/// 指向临时目录
4. 清理前扫描：临时克隆删除前运行
   python .agents/scripts/check-source-path-stability.py --target <待删目录>
   rc=0（零引用）才放行删除；rc=1 先迁移引用
5. 持久性验证：文档定稿后运行 audit 模式
   python .agents/scripts/check-source-path-stability.py
   rc=0 通过；复盘报告事实表等历史时点快照中的临时路径属预期命中，
   按"历史记录 vs 活动引用"判据人工分流

预检通过前不进入 R 阶段。
```

## R阶段：源码阅读与事实采集

```
请帮我学习项目 `<源码路径>`，生成符合OKF v0.2规范的Wiki教程到 `<输出bundle路径>`，
遵循 `<规范文件路径>` 的格式要求。

【R阶段：源码阅读与事实采集】
1. 首先列出源码目录结构，识别所有核心模块文件
2. 逐个阅读核心模块源码，提取可验证的事实（类定义、方法签名、参数、数据流、继承关系）
3. 所有事实编号为 F-xxx，写入 `<spec-dir>/facts.md`
4. 每个事实必须指向具体文件路径，禁止推测和编造

事实采集模板：
F-001: <模块名> - <类/函数名> 定义于 <文件路径>，继承自 <父类>
F-002: <类>.<方法> 接受参数 (<参数列表>)，返回 <返回类型>
F-003: <模块A> 中的 <对象> 被 <模块B> 的 <方法> 引用，传递 <数据>

【质量门】事实中不允许出现"用于"、"目的是"、"设计为"等推断性表述，只记录"代码里有什么"。

事实采集完成后，将事实清单提供给我确认，然后进入下一阶段。
```

## I阶段：架构洞察

```
基于 facts.md 中的 <N> 个事实，提炼架构洞察和知识结构：

1. 提炼3-5个核心架构洞察，每个包含：
   - 陈述：一句话说清架构特征
   - 证据：引用哪些F-xxx事实
   - 反常识：初学者容易误解的点
   - 行动：对文档组织的指导意义

2. 设计知识地图：概念文档分组（入门/核心/高级）、文档依赖关系和学习路径

3. 确定文档清单：concepts/examples/references 各需要哪些文件，每个概念文档覆盖哪些F-xxx事实

将洞察和知识地图写入 `<spec-dir>/insights.md`。
```

## E阶段：批量生成文档

```
请生成OKF规范的中文Markdown文档，遵循以下规则：

【格式规则】
- YAML frontmatter必须包含：type, title, description, tags, generated, verified, status, stale_after, sources
- sources: 指向 references/ 下已存在的信源文件（信源先行，references/已生成完毕）
- 交叉链接使用 / 开头的bundle-relative路径（如 /concepts/02-task-basics.md）
- 中文撰写，英文术语保留并首次出现时括号注释
- 每个文档结尾有"## 相关概念"章节
- 代码块标注语言，API调用必须与 facts.md 中的事实一致
- 禁止虚构API或行为——拿不准的回到 facts.md 核对，找不到对应事实的不允许写入

【内容要求】
- 每个概念文档500-5000字，用 ## 分节（不使用 #，留给文件标题）
- 开头1-2段概述概念/示例是什么
- 示例文档必须包含完整可运行代码
- 信源文档列出所有核心模块和版本信息

【本次生成范围】
<逐文件列出：文件路径、type、title、description、应覆盖的事实编号>

注意：index.md 不在本批生成范围内——所有内容文档生成完毕后最后统一写index。
```

### E阶段子步骤顺序

1. **先生成 references/ 信源登记**（E阶段第一步，不可跳过）
2. 分批生成 concepts/ 概念文档（每批5-7个，按学习路径顺序）
3. 生成 examples/ 示例文档
4. **最后生成各级 index.md**（根index含okf_version frontmatter，子目录index无frontmatter）

### E阶段：index.md 生成（最后一步）

```
请为 `<bundle路径>` 生成各级 index.md 导航文件（所有内容文档已定稿）。

【硬性规则】每个 index.md 必须同时包含：
1. 人类可读导航——表格/列表链接（给读者）
2. `{toctree}` 指令块（给 Sphinx/CI）——缺失即导航断头，CI 门禁会报"未收录(不可达)"

【各级 toctree 收录范围】
- 根 index.md（含 okf_version frontmatter）：concepts/index、examples/index、references/index、log
- 子目录 index.md（无 frontmatter）：本目录全部内容文件的 stem（按文件名排序，跳过 index.md/readme.md）
- 分组 index.md：各束的 <bundle>/index

【toctree 块格式】
```{toctree}
:hidden:
:maxdepth: 2

<条目1>
<条目2>
```

【生成后验证】运行 `python scripts/check-toctrees.py`（或 `invoke gates.toctrees`），
必须输出"toctree 检查通过"才算完成；报"未收录(不可达)"说明某级 index 缺 toctree 或收录不全。
```

## V阶段：独立审查

```
请对 `<bundle路径>` 下的所有文档执行独立审查：

1. 结构检查：目录结构是否完整，是否有遗漏文件
2. Frontmatter检查：每个文档是否有完整的必填字段（type, title, description, tags, generated, verified, status, stale_after, sources）
3. 链接检查：所有交叉链接的目标文件是否存在（使用Grep/Glob验证）
4. 事实溯源检查：对文档中引用的每个类名/方法名，用Grep在 `<源码路径>` 中验证存在性——这是最关键的检查项
5. 代码示例检查：代码示例语法是否正确，API调用是否匹配源码中的签名
6. Index检查：各级index.md是否完整列出所有对应目录的文件，子目录index不应有frontmatter；**每个index.md（根+子目录+分组）必须含`{toctree}`块**——只有表格链接没有toctree块即导航断头，须追加隐藏toctree收录本目录全部内容文件
7. 虚构API检测：对文档中出现的所有import语句和类实例化，逐一在源码中Grep验证
8. ⚡ 计数断言验证：扫描全部文档中"X个/Y份/Z处/N篇"类数量陈述，
   用 Glob/Grep 独立计数逐项比对（如"15个核心模块"→实际数模块目录/Grep定义；
   "368个文件"→Glob 计数），数字不一致即判定为问题
9. 信源路径稳定性检查：运行
   python .agents/scripts/check-source-path-stability.py
   确认文档中无 temporary 信源引用（历史时点快照除外，需人工标注分流）

输出检查报告，按严重程度（🔴虚构API/🔴计数失真/🟡链接断裂/🟢格式问题）列出发现的问题，然后逐一修复。
修复后重新运行检查，直到所有问题清零。
```

## C阶段：模式萃取

```
回顾本次源码→Wiki工作流的执行过程，萃取可复用模式：

1. 回顾R/I/E/V/C各阶段的顺利点和问题点
2. 记录遇到的虚构API、断链、格式错误等具体问题及修复方式
3. 提炼通用Prompt模板（如有改进，更新现有模板）
4. 补充反模式清单（本次实践中发现的新反模式）
5. 记录跨场景迁移的适用性说明
6. 模式文档存入 docs/retrospective/patterns/methodology-patterns/ai-collaboration/
7. 更新模式库索引
```
