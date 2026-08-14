---
id: awesome-okf-vendor-migration-checklist
---
# awesome-okf 迁移到 vendor/ 作为 Git 子模块 - Verification Checklist

## 前置检查与基线
- [x] 已记录根目录 awesome-okf 的完整 40 位 commit hash
- [x] 已确认 awesome-okf 默认分支为 main
- [x] 已确认 LICENSE 文件内容和许可证类型（MIT）
- [x] 已记录三个现有子模块（flexloop、ark-cli、xuanspace）的状态基线
- [x] 已统计并列出所有包含旧路径 `file:///d:/AI/awesome-okf/` 引用的主权区文件清单（2个文件，41处引用）
- [x] 已确认根目录 awesome-okf 为 untracked 状态，非子模块

## 旧目录清理与子模块添加
- [x] 根目录 awesome-okf/ 已删除，`Test-Path d:\AI\awesome-okf` 返回 false
- [x] `git submodule add -b main https://github.com/yzfly/awesome-okf.git vendor/awesome-okf` 命令成功执行（退出码 0）
- [x] vendor/awesome-okf/ 目录存在且包含 README.md、LICENSE、index.md 等源码文件
- [x] 子模块已 checkout 到迁移前记录的精确 commit hash（f6c706274f9cf1640ae249e2f859f7bb78c375bb，非分支 tip）
- [x] `git submodule status vendor/awesome-okf` 输出以空格开头（正常状态，无前缀 `-`/`+`/`U`）
- [x] `.gitmodules` 文件包含 `[submodule "vendor/awesome-okf"]` 条目，path、url、branch、shallow 配置正确

## 现有子模块保护
- [x] `git submodule status vendor/flexloop` 的 commit hash 与迁移前基线一致（7754e53）
- [x] `git submodule status vendor/ark-cli` 的 commit hash 与迁移前基线一致（51ad883，未初始化状态保留）
- [x] `git submodule status projects/xuanspace` 的 commit hash 与迁移前基线一致（d63f5d0，本地新提交状态保留）
- [x] `.gitmodules` 中 flexloop、ark-cli、xuanspace 三个条目未被修改
- [x] vendor/flexloop/ 和 vendor/ark-cli/ 目录内无意外修改

## 元数据更新验证
- [x] [vendor/AGENTS.md](../../../vendor/AGENTS.md) 子模块路由表包含 awesome-okf 条目
- [x] [vendor/AGENTS.md](../../../vendor/AGENTS.md) 中 awesome-okf 类型标注为 third_party
- [x] [vendor/AGENTS.md](../../../vendor/AGENTS.md) 中 awesome-okf 说明文字准确描述用途（中文 OKF 生态项目）
- [x] [vendor/AGENTS.md](../../../vendor/AGENTS.md) 边界声明表包含 awesome-okf 行，标注为不可修改
- [x] `vendor/README.md` 依赖清单表格包含 awesome-okf 行
- [x] `vendor/README.md` 中 awesome-okf 的版本格式为 `main@<short-commit> (子模块)`（main@f6c70627）
- [x] `vendor/README.md` 中 awesome-okf 的类型、日期、用途字段正确
- [x] `vendor/VERSION.md` 版本表格包含 awesome-okf 行
- [x] `vendor/VERSION.md` 中 awesome-okf 的完整 commit hash、来源 URL、日期、许可证、类型、分支字段填写正确
- [x] `vendor/VERSION.md` 更新记录章节有 2026-08-06 引入 awesome-okf 的条目
- [x] 所有 Markdown 表格格式正确，列数与现有行一致，无语法错误

## 路径引用更新验证
- [x] 主权区（排除 vendor/ 和 .trae/specs/规划文件）Grep 搜索 `file:///d:/AI/awesome-okf/` 返回 0 个结果
- [x] 主权区 Grep 搜索 `file:///d:/AI/vendor/awesome-okf/` 的结果数量与旧路径引用统计一致（41处）
- [x] 抽样检查 01-facts.md，file:/// 链接已更新且格式正确（40处）
- [x] 抽样检查 03-patterns.md，file:/// 链接已更新且格式正确（1处）
- [x] 正文中的文字提及（如"awesome-okf 项目"、"yzfly/awesome-okf"）未被误替换
- [x] 非 file:/// 格式的 awesome-okf 提及（如 GitHub URL、分析文档标题）未被修改

## 合规检测
- [x] `python .agents/scripts/check-vendor.py --deep` 执行成功
- [x] check-vendor.py 输出 awesome-okf 相关检查无 ERROR 级别问题（唯一 WARNING 是 ark-cli 未初始化，为预先存在状态）
- [x] check-vendor.py 正确识别 awesome-okf 为 third_party 类型子模块
- [x] awesome-okf 子模块工作树干净，无本地修改

## Git 状态最终验证
- [x] `git status` 显示 .gitmodules 为 modified
- [x] `git status` 显示 vendor/awesome-okf 为 new file（mode 160000 gitlink）
- [x] `git status` 显示 vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 为 modified
- [x] `git status` 显示所有路径更新的主权区 .md 文件为 modified（01-facts.md、03-patterns.md）
- [x] `git diff --cached --name-only` 仅列出预期文件，无意外暂存内容（共7个文件）
- [x] `git submodule status` awesome-okf 显示正常（空格前缀）；ark-cli 未初始化（预先存在）、xuanspace 有本地提交（预先存在）
- [x] 根目录无 awesome-okf/ 残留目录或文件
- [x] **未执行 git commit**（提交需用户确认后执行）
- [x] 所有暂存变更通过三查暂存法验证（查新增、查修改、查删除）
- [x] .gitmodules.backup 临时备份文件已清理

## 可维护性验证
- [x] awesome-okf 分类为 third_party（第三方只读），未创建 vendor/awesome-okf/AGENTS.md
- [x] 未修改 vendor/awesome-okf/ 内的任何文件
- [x] 子模块配置使用 HTTPS URL（https://github.com/yzfly/awesome-okf.git），与原配置一致
- [x] shallow = true 已配置，保持浅克隆
