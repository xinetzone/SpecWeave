---
id: okf-libs-vendor-migration-tasks
---
# 将 .chaos/libs 下三个 OKF 目录迁移为 vendor git 子模块 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 前置检查与基线记录
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 验证 Git 可用，可通过 SSH 访问 GitHub
  - 记录三个源仓库的完整 commit hash 与主分支：
    - `.chaos/libs/awesome-okf` → `ebe906b71fbf68b0b1ecbba58bdad1b4605b297f`（main）
    - `.chaos/libs/awesome-okf-kit` → `5e862eeb8af32595884fe4147faee0deb86fb52b`（main）
    - `.chaos/libs/okf-bundle-template` → `a0883c7bb125efe79b0efaeb8cbd0484abfbd7f5`（main）
  - 确认三个源仓库工作树干净（`git status --short` 为空）
  - 确认 `.chaos/` 未被主仓库跟踪（`git ls-files .chaos` 为空）
  - 确认 `vendor/awesome-okf-bundle`、`vendor/awesome-okf-kit`、`vendor/okf-bundle-template` 三个目标路径不存在
  - 记录现有五个子模块的状态基线：`git submodule status`
  - 确认 `okf-bundle-template` 的许可证（无 LICENSE，检查 NOTICE.md）
  - 统计需要更新相对链接的文件与行（`01-ecosystem-map.md` 中 3 处）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-1.1: 获取到三个完整 commit hash（40位 SHA）
  - `programmatic` TR-1.2: 三个源仓库 `git status --short` 输出为空
  - `programmatic` TR-1.3: `git ls-files .chaos` 输出为空
  - `programmatic` TR-1.4: 三个目标路径 `Test-Path` 返回 false
  - `programmatic` TR-1.5: `git submodule status` 记录五个现有子模块状态
  - `human-judgement` TR-1.6: 确认 okf-bundle-template 许可证类型（读 NOTICE.md）
- **Notes**: commit hash 必须精确记录，确保子模块检出到完全相同的版本

## [x] Task 2: 移除 .chaos/libs 下三个源目录
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 确认三个源目录确实是未跟踪状态（非子模块，非主仓库文件）
  - 删除 `.chaos/libs/awesome-okf`、`.chaos/libs/awesome-okf-kit`、`.chaos/libs/okf-bundle-template`
  - 验证三个路径不再存在
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 删除命令退出码为 0
  - `programmatic` TR-2.2: `Test-Path` 对三个路径返回 false
- **Notes**: 删除前务必备份 commit hash；如误删可从远程重新克隆

## [x] Task 3: 添加三个 git 子模块到 vendor
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 执行三个 `git submodule add -b main <url> vendor/<name>`：
    - `git submodule add -b main git@github.com:linyiru/awesome-okf.git vendor/awesome-okf-bundle`
    - `git submodule add -b main git@github.com:vinodborole/awesome-okf-kit.git vendor/awesome-okf-kit`
    - `git submodule add -b main git@github.com:vinodborole/okf-bundle-template.git vendor/okf-bundle-template`
  - 进入每个子模块目录，checkout 到 Task 1 记录的精确 commit hash
  - 如需要，配置 `.gitmodules` 中 `shallow = true`（与 awesome-okf(yzfly) 先例保持一致）
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: 三个 `git submodule add` 命令退出码均为 0
  - `programmatic` TR-3.2: 三个 vendor/ 目标目录存在且含对应上游源码
  - `programmatic` TR-3.3: .gitmodules 包含三个新条目
  - `programmatic` TR-3.4: 三个子模块 `rev-parse HEAD` 输出与 Task 1 记录一致
  - `programmatic` TR-3.5: `git submodule status` 三个新子模块输出以空格开头（正常状态）
- **Notes**: 必须 checkout 到精确 commit 而非分支 tip，确保分析文档引用有效

## [x] Task 4: 验证现有子模块未受影响
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 执行 `git submodule status` 检查所有子模块
  - 对比 Task 1 记录的五个现有子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog、xuanspace）的 commit hash
  - 确认 .gitmodules 中这五个子模块的配置未被修改
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-4.1: 五个现有子模块 commit hash 与 Task 1 基线一致
  - `programmatic` TR-4.2: .gitmodules 中五个旧子模块条目未变更
- **Notes**: 如发现现有子模块状态被意外修改，立即暂停并回滚

## [x] Task 5: 更新 vendor/AGENTS.md 路由表与边界声明
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 读取当前 vendor/AGENTS.md
  - 在「子模块路由表」表格添加三行：
    - awesome-okf-bundle（third_party，无 AGENTS.md 入口，说明：linyiru/awesome-okf 上游 OKF Awesome 列表与 bundle 构建器）
    - awesome-okf-kit（third_party，无 AGENTS.md 入口，说明：OKF bundle 注册表工具集）
    - okf-bundle-template（third_party，无 AGENTS.md 入口，说明：OKF bundle 发布模板）
  - 在「边界声明」表格添加三行（归属对应子模块，可修改 ❌ 否）
  - 保持 Markdown 表格格式一致
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 子模块路由表新增三行，列数与现有行一致
  - `human-judgement` TR-5.2: 三行类型均正确标注为 third_party
  - `human-judgement` TR-5.3: 边界声明表新增三行
  - `programmatic` TR-5.4: Markdown 表格语法正确，无列数不匹配
- **Notes**: 参考现有 ark-cli / awesome-okf 行格式（同为 third_party 类型）

## [x] Task 6: 更新 vendor/README.md 依赖清单
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 读取当前 vendor/README.md
  - 在依赖清单表格添加三行：
    - awesome-okf-bundle: `main@ebe906b7 (子模块)`、third_party、2026-08-06、linyiru/awesome-okf 上游 OKF 列表与 bundle 构建器
    - awesome-okf-kit: `main@5e862eeb (子模块)`、third_party、2026-08-06、OKF bundle 注册表工具集
    - okf-bundle-template: `main@a0883c7b (子模块)`、third_party、2026-08-06、OKF bundle 发布模板
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 依赖清单表格新增三行，字段完整
  - `programmatic` TR-6.2: Markdown 表格列数与现有行一致
- **Notes**: 版本格式与 awesome-okf(yzfly) 条目保持一致

## [x] Task 7: 更新 vendor/VERSION.md 版本记录
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 读取当前 vendor/VERSION.md
  - 在版本表格添加三行（完整 commit hash、来源 URL、日期 2026-08-06、许可证、类型 third_party、跟踪分支 main）：
    - awesome-okf-bundle: ebe906b71fbf68b0b1ecbba58bdad1b4605b297f、git@github.com:linyiru/awesome-okf.git、CC0-1.0
    - awesome-okf-kit: 5e862eeb8af32595884fe4147faee0deb86fb52b、git@github.com:vinodborole/awesome-okf-kit.git、MIT
    - okf-bundle-template: a0883c7bb125efe79b0efaeb8cbd0484abfbd7f5、git@github.com:vinodborole/okf-bundle-template.git、依 Task 1 确认
  - 在「更新记录」章节添加条目：`- 2026-08-06 | 引入 awesome-okf-bundle、awesome-okf-kit、okf-bundle-template 子模块（从 .chaos/libs/ 迁移至 vendor/，修复架构边界）`
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 版本表格新增三行，字段完整准确
  - `human-judgement` TR-7.2: 更新记录章节有 2026-08-06 对应条目
  - `programmatic` TR-7.3: Markdown 表格列数与现有行一致
- **Notes**: 注意版本表格和更新记录是两种不同格式

## [x] Task 8: 修复主权区文档的失效相对链接
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 读取 `okf-ecosystem-wiki/01-ecosystem-map.md`
  - 将其中 3 处 `.chaos/libs/awesome-okf/` 替换为 `vendor/awesome-okf-bundle/`，保持 `../../../../../../../` 相对前缀不变
  - 均为文件链接（README.md、bundle/index.md、scripts/build-okf-bundle.mjs）
  - 替换后验证 Markdown 链接格式未被破坏
  - 说明：`02-bundle-registry.md`、`03-bundle-template.md` 的 frontmatter `source:` 仅为文本描述（非文件链接），无需修改
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-8.1: Grep 搜索 `01-ecosystem-map.md`，`.chaos/libs/awesome-okf/` 出现次数为 0
  - `programmatic` TR-8.2: Grep 搜索 `vendor/awesome-okf-bundle/` 出现次数为 3
  - `human-judgement` TR-8.3: 抽样检查，确认相对前缀未变、链接格式正确
- **Notes**: 使用精确字符串替换，避免破坏正文

## [x] Task 9: 运行 check-vendor.py 合规检测
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 7, Task 8
- **Description**:
  - 运行 `python .agents/scripts/check-vendor.py --deep` 进行深度合规检测
  - 如检测出问题，根据错误信息修复后重新运行
  - 记录检测结果
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-9.1: check-vendor.py --deep 退出码为 0
  - `programmatic` TR-9.2: 输出无 ERROR 级别的问题
  - `human-judgement` TR-9.3: 如有 WARNING 需评估是否可接受
- **Notes**: check-vendor.py 会验证子模块配置、元数据一致性、非法引用等

## [x] Task 10: 暂存所有变更并最终验证
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 按三查暂存法逐个添加文件：
    1. 查修改：.gitmodules、vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md、01-ecosystem-map.md
    2. 查新增：vendor/awesome-okf-bundle、vendor/awesome-okf-kit、vendor/okf-bundle-template 三个 gitlink
    3. 查删除：确认 .chaos/libs/ 下三个源目录已移除
  - 执行 `git add` 逐个添加（禁止 `git add .`）
  - 验证暂存区内容：`git diff --cached --name-only`
  - 验证最终状态：`git status`、`git submodule status`
  - 执行链接检查（至少检查更新过的 01-ecosystem-map.md 中的链接）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: `git diff --cached --name-only` 列出所有预期变更文件，无意外
  - `programmatic` TR-10.2: `git submodule status` 八个子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog、xuanspace、awesome-okf-bundle、awesome-okf-kit、okf-bundle-template）均显示正常（空格前缀）
  - `programmatic` TR-10.3: 暂存的三个新条目 mode 为 160000（gitlink）
  - `programmatic` TR-10.4: `.chaos/libs/` 下三个源目录无残留
  - `human-judgement` TR-10.5: `git diff --cached` 审查暂存内容无误
- **Notes**: 不执行 git commit，仅暂存；最终提交由用户确认后执行

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 4]
- [Task 7] depends on [Task 4]
- [Task 8] depends on [Task 4]
- [Task 9] depends on [Task 5, Task 6, Task 7, Task 8]
- [Task 10] depends on [Task 9]