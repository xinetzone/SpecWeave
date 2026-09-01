# Checklist

> 验证目标：学科分类重构后，`doc/bundles/` 学科导航成立、零断链、内容无损、门控全绿、提交原子化。

## 目录结构
- [x] `doc/bundles/` 顶层仅存 9 个目录：guoxue、zhexue、kexue、wenxue、yixue、sheke、yishu、jishu、meta
- [x] 每个学科域含 `index.md`（`type: group`，学科定义 + 域内导航 + toctree）
- [x] 42 组全部归位，无遗漏、无错放；`think/`、`tcm/`、`workplace/`、`science/` 旧域目录已删除
- [x] `meta/` 锚点路径不变
- [x] 归属裁决正确：佛学/算学在国学、西方数学在科学、黄帝内经/道医/养生/房中在医学、性学/两性/职场在社会科学、声乐在艺术、psi 在哲学

## 链接与内容
- [x] 根绝对跨组链接已按新路径更新，无残留旧前缀（`](/think/`、`](/tcm/`、`](/science/`、`](/workplace/` 及 12 个技术域旧前缀清零）
- [x] 相对跨组链接已按新层级调整，无迁移引入断链（129 断链经旧路径反查全部为存量）
- [x] 组内相对链接未受影响（整子树迁移）
- [x] 所有束内容文档无内容变更（7231 纯重命名 + 65 个仅链接变更，经链接剥离比对验证），378 束总数不变

## 索引一致性
- [x] 根 `bundles/index.md` 为 8 学科域 + 1 锚点导航，frontmatter 计数与门控重算值一致（378/43/9）
- [x] `doc/index.md` 计数与实际一致（不再残留 297/14/37 旧值）
- [x] 生态关系概览图与推荐入门路径按学科体系更新
- [x] `doc/bundles/.gitignore` 已改为 `!jishu/build/`，`git check-ignore` 验证 build 分组可跟踪

## 构建与等价性
- [x] 三门全绿（utf8 + toctrees + bundles；invoke 缺 invocations 模块，直调脚本等价执行）
- [x] `sphinx-build -b dummy -E doc _build/dummy` 无迁移引入错误（残留 ERROR/WARNING 经 9 文件字节级哈希核对为存量问题）
- [x] 全量 Markdown 链接检查：迁移零引入断链（存量 129 断链如实记录，不在本次射程）
- [x] `git status` 仅含预期变更，无意外删除；提交后工作树干净

## 提交原子化
- [x] 三段式提交（abff22de 结构重命名批 / 452016f0 链接修复批 / 5d72953e 索引批），单一职责，Conventional Commits 中文主题
- [x] 每次提交前已核对暂存集（`git diff --cached --name-only`），无并行会话文件混入
- [x] 提交历史可追溯（`git mv` 保留 rename 历史）
- [x] 主仓库子模块指针已 bump（2bee21e23）并推送，子模块先行推送纪律已遵守（8b976825..5d72953e）
