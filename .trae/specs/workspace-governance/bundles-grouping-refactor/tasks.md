# Tasks

> 目标仓库：`projects/awesome-okf-xs`（git submodule，重构全部在其内部进行，使用 `git mv`）
> 方法论：七概念场景3（重构优化）I→F→A→V→C

- [x] Task 1: 基线盘点（R/I 产出）
  - [x] 枚举 `doc/bundles/` 顶层目录全集（预期 28 组），核对每组束数、是否含组 `index.md`
  - [x] 用 grep 生成跨组链接清单（根绝对 `](/group/` 与相对 `](../group/` 两类），按组分组计数
  - [x] 记录根 [index.md](../../projects/awesome-okf-xs/doc/bundles/index.md) 与 [doc/index.md](../../projects/awesome-okf-xs/doc/index.md) 现有计数与导航表差异
  - [x] 产出盘点报告，作为 Task 4/6 的修复依据
- [x] Task 2: 建立 10 个域目录骨架
  - [x] 创建域目录（meta、python 已在原地复用；新建 build、document、data、ml、ai、comm、web、think）
  - [x] 为每个域编写 `index.md`（`type: group`，含域说明与域内分组导航占位）
- [x] Task 3: 迁移组到域下（按域分批，每批一次原子提交）
  - [x] 域 `ai`：迁移 agnes-ai、ai-agent、langchain-ai、datawhale、coze、deepseek、trae、tencent、pocketflow → `ai/`
  - [x] 域 `build`：迁移 conda、cmake、tooling → `build/`（scikit-build 原地作锚点）
  - [x] 域 `document`：迁移 sphinx、myst、jupyter-book、katex、jupyter → `document/`
  - [x] 域 `comm`：迁移 messaging、networking → `comm/`
  - [x] 域 `web`：迁移 fastapi、graphql → `web/`
  - [x] 域 `data`/`ml`/`think`：迁移 pydata → `data/`、onnx → `ml/`、psi/laozi → `think/`
  - [x] 每批迁移后用 `git status` 确认仅含预期移动（`git mv` 不丢历史），组内相对链接未受影响
- [x] Task 4: 修复根绝对跨组链接（旧估 ~224 处，真值 1616 处）
  - [x] 对每个迁移组，批量替换 `](/<group>/` → `](/<domain>/<group>/`（注意 `build/scikit-build` 等原地锚点组无需前缀）
  - [x] 处理 `]\(/<group>...` 变体与带锚点/参数的链接
- [x] Task 5: 修复相对跨组链接（旧估 ~121 处，真值 188 处）
  - [x] 按文件深度逐个调整 `](../<group>/...` 为指向新域的路径
  - [x] 修复各域内组 `index.md` 指向其他组的相对链接
  - [x] 修正：Task 4/5 合计真值 1804 处（1616 根绝对 + 188 相对），经内容哈希分类精确验证
- [x] Task 6: 重写根索引 [bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md)
  - [x] 改为「域导航 + 域内分组导航」两级结构
  - [x] 补齐缺失组（含 coze/deepseek/trae/tencent/myst 等），修正 `total_bundles`/`groups` 为实际值（248 束 / 28 组 / 10 域）
  - [x] 更新「生态关系概览」「推荐入门路径」中的组路径
- [x] Task 7: 更新 Sphinx 入口 [doc/index.md](../../projects/awesome-okf-xs/doc/index.md)
  - [x] 修正「N 组 / M 束」计数与实际一致（248 束 / 28 组 / 10 域）
- [x] Task 8: 全量验证（V 阶段等价性验证）
  - [x] 链接检查：全部 Markdown 交叉引用 0 断链（重构引入 0 新断链，根绝对 1616 + 相对 188 = 1804 处修复）
  - [x] Sphinx 构建：`sphinx-build -b dummy -E doc _build/dummy doc/index.md` 通过无致命错误
  - [x] 束完整性：抽样核对迁移后束的 `index.md`/`log.md` 内容未变
  - [x] git 状态核对：无意外删除；`build/` 域在 `.gitignore`（`!build/`）下正常被跟踪
- [x] Task 9: 原子提交收尾（C 阶段）
  - [x] 按域分批 + 索引更新分批，每个提交单一职责、Conventional Commits 中文主题
  - [x] 预提交验证（链接/格式）通过后提交
  - [x] 三批提交：`c02bb5e`（结构重命名 4666 rename + 9 域索引）、`929bda7`（401 链接修复）、`fd124f7`（根索引）；工作树已干净

# Task Dependencies
- [Task 1] 无依赖（前置基线）
- [Task 2] 依赖 [Task 1]（需盘点确认域名与收录组）
- [Task 3] 依赖 [Task 2]（域目录就绪后可迁移）
- [Task 4]/[Task 5] 依赖 [Task 3]（迁移完成后修复断链）
- [Task 6]/[Task 7] 依赖 [Task 1] 盘点数据与 [Task 3] 迁移结果
- [Task 8] 依赖 [Task 4]/[Task 5]/[Task 6]/[Task 7]
- [Task 9] 依赖全部前置任务
