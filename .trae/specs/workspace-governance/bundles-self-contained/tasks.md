# Bundles 自包含自洽化重构 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 批量修复缺失 .md 后缀的链接
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 编写 Python 脚本批量扫描 bundles/ 目录下所有 Markdown 文件
  - 识别所有以 `/concepts/`、`/examples/`、`/references/` 开头但缺少 `.md` 后缀的链接
  - 在链接末尾补充 `.md` 后缀（保留锚点 `#section` 部分）
  - 同时修复 frontmatter 中 sources 字段的路径（如 `/references/source` → `/references/source.md`）
  - 注意不要误伤代码块、外部 URL、或已经带 `.md` 后缀的链接
  - 优先修复：home-assistant、apache-tvm、ai-agent-skills、tuya-iot、okf-ecosystem、mobile-use、veadk-python、english-grammar、laozi-lineage
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: 脚本运行后，Grep 搜索 `\(/concepts/[^)]*[^.md)]\)` 无匹配（不包括锚点）
  - `programmatic` TR-1.2: Grep 搜索 `\(/examples/[^)]*[^.md)]\)` 无匹配
  - `programmatic` TR-1.3: Grep 搜索 `\(/references/[^)]*[^.md)]\)` 无匹配
  - `programmatic` TR-1.4: check-links.py 扫描时 broken_local 数量显著减少（从 545 降至接近 0）
  - `human-judgement` TR-1.5: 抽查 20 个修复后的链接，确认 .md 后缀添加正确且锚点保留
- **Notes**: 使用正则批量替换时需注意排除代码块内的内容；参考 check-links.py 中的 is_code_fence_context 函数

## [ ] Task 2: 清理 apache-tvm 中的 file:/// 本地绝对路径
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 读取 `bundles/chaos/apache-tvm/references/facts-relax-te-topi.md`
  - 识别所有 `file:///d:/AI/.chaos/...` 形式的本地绝对路径
  - 这些路径是开发过程中记录源码位置的引用，应移除或替换为 bundle-relative 说明
  - 检查其他文件是否也存在 file:/// 路径（先 Grep 确认范围）
  - 如果路径仅用于标注"源码行号"，可简化描述或删除具体路径
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: Grep -r "file:///" bundles/ 无匹配结果
  - `human-judgement` TR-2.2: 检查 facts-relax-te-topi.md，确认移除绝对路径后事实描述仍然完整可读
- **Notes**: 这些路径在非作者机器上完全无效，必须清理以保证可移植性

## [ ] Task 3: 删除重复的 verification-report.md
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 删除以下重复文件（保留 bundle 根目录版本，删除 references/ 下的副本）：
    - `bundles/chaos/mobile-use/references/verification-report.md`
    - `bundles/chaos/okf-ecosystem/references/verification-report.md`
    - `bundles/chaos/veadk-python/references/verification-report.md`
  - 删除前确认根目录版本存在且内容完整
  - 检查是否有文件引用了 references/ 下的 verification-report.md，如有则更新引用路径
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: Glob 搜索 bundles/**/verification-report.md 只返回 7 个结果（每个标准 bundle 根目录一个）
  - `programmatic` TR-3.2: 上述三个 references/ 路径下无 verification-report.md 文件
  - `programmatic` TR-3.3: 检查是否有链接指向被删除的文件，确保零断链
- **Notes**: 根目录版本与 log.md 同级，符合 PATTERNS_LESSONS.md 中的建议位置

## [ ] Task 4: 创建 bundles/chaos/index.md 分类入口
- **Priority**: high
- **Depends On**: Task 1（链接需带 .md 后缀）
- **Description**: 
  - 参考 tiktoken/index.md 的格式和风格
  - 创建 bundles/chaos/index.md，列出 chaos 分类下所有 10 个 bundle：
    - ai-agent-skills
    - apache-tvm
    - english-grammar
    - home-assistant
    - laozi-lineage
    - mobile-use
    - okf-ecosystem
    - tiktoken
    - tuya-iot
    - veadk-python
  - 为每个 bundle 提供简短的一句话简介（从各 bundle 的 index.md description 字段提取）
  - 使用正确的相对路径（如 `./tiktoken/index.md`）链接到各 bundle
  - 添加适当的 frontmatter（okf_version、title、description 等，参考 tiktoken 格式）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: bundles/chaos/index.md 文件存在
  - `programmatic` TR-4.2: 文件中的所有链接可通过 check-links.py 验证
  - `human-judgement` TR-4.3: 每个 bundle 都有条目、简介和可点击链接，格式统一美观
- **Notes**: chaos 是当前唯一的分类，未来可能有其他分类

## [ ] Task 5: 创建 bundles/index.md 总入口
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 创建 bundles/index.md 作为知识包集合的总入口
  - 列出分类：目前仅有 chaos/ 分类
  - 提供简短的说明：这是什么、包含哪些类型的知识包、如何导航
  - 链接到 bundles/chaos/index.md
  - 如果需要，可提及 projects/awesome-okf-xs/doc/bundles/ 作为 OKF 官方知识库参考（用外部链接或说明文字，不要用相对路径指向 projects/ 外部）
  - 添加适当的 frontmatter
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: bundles/index.md 文件存在
  - `programmatic` TR-5.2: 文件中的链接指向 bundles/ 内部（./chaos/index.md），不指向 bundles/ 外部的本地文件
  - `human-judgement` TR-5.3: 入口页面清晰易懂，新用户可快速理解如何导航
- **Notes**: 保持简洁，作为导航入口不需要过多内容

## [ ] Task 6: 全量链接验证与收尾修复
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**: 
  - 运行 `python .agents/scripts/check-links.py --path bundles --check-frontmatter-paths`
  - 检查并修复任何剩余的断链（broken_local、warning_local、broken_frontmatter）
  - 可能的遗留问题：
    - laozi-lineage 内部链接（它使用不同的目录结构）
    - english-grammar 内部链接
    - 目录链接（指向概念目录而非具体文件）
    - frontmatter 中 sources 字段的路径遗漏
  - 所有目录链接应链接到对应目录的 index.md（如 `concepts/` → `concepts/index.md`）
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: check-links.py 输出显示 "通过: 所有本地引用均存在"
  - `programmatic` TR-6.2: broken_local = 0, warning_local = 0, broken_frontmatter = 0
  - `programmatic` TR-6.3: 没有链接指向 bundles/ 外部的本地文件（外部 HTTP 链接除外）
  - `human-judgement` TR-6.4: 抽查 bundles/index.md → bundles/chaos/index.md → 各 bundle index.md 的导航路径，确认可完整导航
- **Notes**: 这是质量门禁任务，必须确保零错误才能收尾
