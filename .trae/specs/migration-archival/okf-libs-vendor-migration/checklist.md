---
id: okf-libs-vendor-migration-checklist
---
# 将 .chaos/libs 下三个 OKF 目录迁移为 vendor git 子模块 - Verification Checklist

## 前置检查与基线
- [x] 已记录三个源仓库的完整 40 位 commit hash（ebe906b7、5e862eeb、a0883c7b）
- [x] 已确认三个源仓库默认分支均为 main
- [x] 已确认三个源仓库工作树干净（git status --short 为空）
- [x] 已确认 `.chaos/` 未被主仓库 git 跟踪（`git ls-files .chaos` 为空）
- [x] 已确认 vendor/awesome-okf-bundle、vendor/awesome-okf-kit、vendor/okf-bundle-template 三个目标路径不存在
- [x] 已记录五个现有子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog、xuanspace）的状态基线
- [x] 已确认 okf-bundle-template 许可证类型（读 NOTICE.md）

## 源目录清理与子模块添加
- [x] `.chaos/libs/awesome-okf`、`.chaos/libs/awesome-okf-kit`、`.chaos/libs/okf-bundle-template` 已删除，`Test-Path` 返回 false
- [x] 三个 `git submodule add -b main <url> vendor/<name>` 命令成功执行（退出码 0）
- [x] vendor/awesome-okf-bundle、vendor/awesome-okf-kit、vendor/okf-bundle-template 目录存在且含上游源码
- [x] 三个子模块已 checkout 到迁移前记录的精确 commit hash（非分支 tip）
- [x] `.gitmodules` 文件包含三个新条目，path、url、branch 配置正确
- [x] 三个新子模块 `git submodule status` 输出以空格开头（正常状态，无前缀 `-`/`+`/`U`）

## 现有子模块保护
- [x] `git submodule status` 五个现有子模块 commit hash 与迁移前基线一致
- [x] vendor/flexloop、vendor/ark-cli、vendor/awesome-okf、vendor/knowledge-catalog、projects/xuanspace 目录内无意外修改
- [x] `.gitmodules` 中五个旧子模块条目未被修改

## 元数据更新验证
- [x] vendor/AGENTS.md 子模块路由表包含三个新条目
- [x] vendor/AGENTS.md 中三个新条目类型均标注为 third_party
- [x] vendor/AGENTS.md 边界声明表包含三个新行，标注为不可修改
- [x] vendor/README.md 依赖清单表格包含三个新行
- [x] vendor/README.md 中三个新行的版本格式为 `main@<short-commit> (子模块)`（ebe906b7、5e862eeb、a0883c7b）
- [x] vendor/README.md 中三个新行的类型、日期、用途字段正确
- [x] vendor/VERSION.md 版本表格包含三个新行
- [x] vendor/VERSION.md 中三个新行的完整 commit hash、来源 URL、日期、许可证、类型、分支字段填写正确
- [x] vendor/VERSION.md 更新记录章节有 2026-08-06 引入三个子模块的条目
- [x] 所有 Markdown 表格格式正确，列数与现有行一致，无语法错误

## 相对链接更新验证
- [x] `01-ecosystem-map.md` 中原 `.chaos/libs/awesome-okf/` 的 3 处文件链接已替换为 `vendor/awesome-okf-bundle/`
- [x] 替换后 `../../../../../../../` 相对前缀保持不变
- [x] 抽样检查，Markdown 链接格式正确、正文未被误替换
- [x] `02-bundle-registry.md`、`03-bundle-template.md` 的 frontmatter `source:` 文本（非文件链接）未误改

## 合规检测
- [x] `python .agents/scripts/check-vendor.py --deep` 执行成功（退出码 0）
- [x] check-vendor.py 输出三个新子模块相关检查无 ERROR 级别问题
- [x] check-vendor.py 正确识别三个新子模块为 third_party 类型
- [x] 三个新子模块工作树干净，无本地修改

## Git 状态最终验证
- [x] `git status` 显示 .gitmodules 为 modified
- [x] `git status` 显示三个新子模块为 new file（mode 160000 gitlink）
- [x] `git status` 显示 vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md、01-ecosystem-map.md 为 modified
- [x] `git diff --cached --name-only` 仅列出预期文件，无意外暂存内容
- [x] `git submodule status` 所有子模块显示正常
- [x] `.chaos/libs/` 下三个源目录无残留
- [x] **未执行 git commit**（提交需用户确认后执行）
- [x] 所有暂存变更通过三查暂存法验证（查新增、查修改、查删除）

## 可维护性验证
- [x] 三个新子模块分类为 third_party（第三方只读），未创建 vendor/<name>/AGENTS.md
- [x] 未修改三个新子模块内的任何文件
- [x] 现有 vendor/awesome-okf（yzfly）子模块配置与内容未受影响，与 vendor/awesome-okf-bundle（linyiru）共存无冲突
- [x] 子模块配置使用 SSH URL（git@github.com:...），与原配置一致