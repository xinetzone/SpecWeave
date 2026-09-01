# Tasks

> 目标仓库：`projects/awesome-okf-xs`（git submodule，全部重构在其内部，使用 `git mv`）
> 方法论：七概念场景3（重构优化）I→F→A→V→C；I/F 已在 spec.md 完成，以下为 A→V→C 实施任务
> 纪律：子模块有并行会话——`git add` 与 `git commit` 必须分两次调用，中间 `git diff --cached --name-only` 核对暂存集；发现非己方文件立即停止并报告

- [x] Task 1: 基线盘点与映射冻结（A 前置）
  - [x] 枚举 `doc/bundles/` 现有 17 域 / 75 组 / 363 束全集，与根索引计数核对（门控基线：17 域/75 组/363 束五面一致；invoke 缺 invocations 模块，改用 `python scripts/check-*.py` 直调）
  - [x] 按 spec.md F 阶段映射表生成「旧路径→新路径」完整清单（42 组逐条），人工复核归属无歧义
  - [x] 统计两类跨组链接基线：根绝对 `](/` 834 处/165 文件；相对 `](../` 1022 处/361 文件（含组内链接，实际修复量以实施为准）
  - [x] 检查子模块工作树状态：工作树干净、无 MERGE_HEAD，可安全开工
- [x] Task 2: 创建 8 个学科域骨架
  - [x] 新建目录：guoxue、zhexue、kexue、wenxue、yixue、sheke、yishu、jishu
  - [x] 为每域编写 `index.md`（`type: group`，含学科定义、收录边界、域内分组导航占位、隐藏 toctree 占位）
- [x] Task 3: 物理迁移（按学科域分批，每批 `git mv` 后单独提交）
  - [x] 批1 国学：think 下 15 组（confucian/confucius/laozi/zhuangzi/mozi/yinyangjia/zhouyi/hetu-luoshu/legalism/huangdi/buddhism/guiguzi/daojia/yangming/suanxue）→ `guoxue/`
  - [x] 批2 哲学：think/psi → `zhexue/`
  - [x] 批3 科学：science/{chemistry,physics} + think/math → `kexue/`
  - [x] 批4 文学：think/classics → `wenxue/`
  - [x] 批5 医学与养生：tcm（整域含 guide.md/changelog.md）+ think/{huangdi-neijing,medicine,daoyi,yangsheng,fangzhong} → `yixue/`
  - [x] 批6 社会科学：workplace + think/{relationships,sexology} → `sheke/`
  - [x] 批7 艺术：think/vocal → `yishu/`
  - [x] 批8 技术：12 个技术域（ai/document/build/comm/containers/ml/data/viz/rust/web/python/terminal）→ `jishu/<域名>/`
  - [x] 迁移后删除空旧域目录与 4 个旧域索引（think/tcm/workplace/science 的 index.md 内容先并入新域索引）
  - [x] 每批后 `git status` 核对仅含预期 rename，无内容丢失
- [x] Task 4: 修复根绝对跨组链接
  - [x] 按映射表批量替换 `](/<旧路径>/` → `](/<新路径>/`（含带锚点/参数变体）
  - [x] 注意：`jishu/` 下技术组互链需加 `jishu/` 前缀；`meta/` 锚点引用不变
  - [x] 逐组抽查替换正确性（防误伤正文中非链接文本）
- [x] Task 5: 修复相对跨组链接
  - [x] 按文件深度逐个调整 `](../<组>/...` 指向新层级
  - [x] 修复各域/组 `index.md` 中指向其他组的相对链接
- [x] Task 6: 重写根索引 `bundles/index.md`
  - [x] 改为「8 学科域 + 1 锚点」导航；更新生态关系概览图与推荐入门路径
  - [x] frontmatter 与计数行取 `invoke gates.bundles` 重算值（实际 378 束 / 43 组 / 9 域，以门控递归计数为准）
  - [x] toctree 更新为 9 域入口
- [x] Task 7: 更新入口与配置
  - [x] `doc/index.md` 计数修正为实际值
  - [x] `doc/bundles/.gitignore`：`!build/` → `!jishu/build/`，`git check-ignore` 验证 build 分组可跟踪
- [x] Task 8: 全量验证（V 阶段等价性验证）
  - [x] 三门全绿（utf8 + toctrees + bundles；invoke 缺 invocations 模块，直调脚本）
  - [x] `sphinx-build -b dummy -E doc _build/dummy` 无致命错误（残留 ERROR/WARNING 经 9 文件字节级哈希核对确认为存量问题，非迁移引入）
  - [x] 全量 Markdown 链接检查：129 断链全部为存量（旧路径下目标亦不存在），迁移零引入
  - [x] 束完整性验证：7296 重命名中 7231 纯重命名，65 个含变更经链接剥离比对证明仅链接调整
  - [x] 378 束总数核对：每束有且仅有一个学科归属（门控五面一致）
- [x] Task 9: 原子提交收尾（C 阶段）
  - [x] 三段式提交：①abff22de 结构重命名批（7231 纯重命名 + 8 域索引 + 2 旧索引删除）②452016f0 链接修复批（65 文件 202 增/202 删对称）③5d72953e 根索引/入口/.gitignore/门控脚本批
  - [x] 每次提交前三查暂存法 + `git diff --cached --name-only` 核对（无并行会话文件混入）
  - [x] Conventional Commits 中文主题，提交后 `git show --stat` 验证
  - [x] 主仓库 bump 子模块指针并推送：用户决策「bump 并推送全部」→ 子模块推送（8b976825..5d72953e）→ 主仓库指针提交 2bee21e23 → 主仓库推送（c75f18b05..2bee21e23）

# Task Dependencies
- [Task 1] 无依赖（前置基线）
- [Task 2] 依赖 [Task 1]
- [Task 3] 依赖 [Task 2]
- [Task 4]/[Task 5] 依赖 [Task 3]
- [Task 6]/[Task 7] 依赖 [Task 3]（迁移结果）与 [Task 1] 盘点数据
- [Task 8] 依赖 [Task 4]/[Task 5]/[Task 6]/[Task 7]
- [Task 9] 依赖全部前置任务
