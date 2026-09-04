# Checklist

> 验证目标：域层重组后，`doc/bundles/` 导航一致、零断链、内容无损、Sphinx 可构建、提交原子化。

## 目录结构
- [x] `doc/bundles/` 顶层出现 10 个域目录：meta、python、build、document、data、ml、ai、comm、web、think
- [x] 每个域目录含 `index.md`（`type: group`）与已归位的组目录
- [x] 28 组全部归入对应域，无遗漏、无错放
- [x] 锚点组路径不变：`meta/okf-spec/`、`python/cpython/`、`build/scikit-build/` 保持原位

## 链接与内容
- [x] 根绝对跨组链接已按 `](/<domain>/<group>/...` 更新，无残留旧前缀
- [x] 相对跨组链接已按新层级调整，无断链
- [x] 组内相对链接未受影响（组整体迁移）
- [x] 所有束的 `index.md`/`log.md` 内容未变（仅路径变化）
- [x] 无内容丢失：迁移前后束文件数一致

## 索引一致性
- [x] 根 [bundles/index.md](../../projects/awesome-okf-xs/doc/bundles/index.md) 导航表覆盖全部域与组，`total_bundles`/`groups` 与实际一致（248/28/10）
- [x] [doc/index.md](../../projects/awesome-okf-xs/doc/index.md) 的「组/束」计数与实际一致
- [x] 生态关系概览、推荐入门路径中的组路径已更新

## 构建与等价性
- [x] Sphinx 构建通过：`sphinx-build -b dummy -E doc _build/dummy doc/index.md` 无致命错误
- [x] Markdown 交叉引用检查 0 断链
- [x] `git status` 仅含预期的移动/新增/修改，无意外删除（提交后工作树干净）
- [x] `build/` 域在 `.gitignore`（含 `!build/`）下正常被 git 跟踪（`git check-ignore` 验证）

## 提交原子化
- [x] 每批迁移/索引更新单独提交，单一职责，Conventional Commits 中文主题
- [x] 提交历史可追溯（`git mv` 保留 rename 历史）
  - [x] `c02bb5e` refactor(bundles): 归组 28 组知识束到 10 个技术域（4666 rename + 9 域索引）
  - [x] `929bda7` fix(bundles): 修复跨组链接指向新域路径（401 文件）
  - [x] `fd124f7` docs(bundles): 更新总索引与入口索引计数
