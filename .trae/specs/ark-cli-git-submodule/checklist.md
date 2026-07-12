# ark-cli Git 子模块集成 - Verification Checklist

## 子模块添加验证
- [ ] `git submodule add` 命令成功执行，退出码为 0
- [ ] `vendor/ark-cli/` 目录存在且包含 ark-cli 源码文件（README.md、package.json 等）
- [ ] `.gitmodules` 文件包含 `[submodule "vendor/ark-cli"]` 条目，path 和 url 正确
- [ ] `git submodule status vendor/ark-cli` 输出状态正常（commit hash 前为空格，无前缀 `-`/`+`/`U`）
- [ ] ark-cli 子模块内文件完整，无空目录或截断

## 现有子模块保护验证
- [ ] `git submodule status vendor/flexloop` 状态与操作前一致，commit hash 未变化
- [ ] `.gitmodules` 中 flexloop 条目保持不变（path、url、branch 均未修改）
- [ ] vendor/flexloop/ 目录内无意外修改

## 元数据更新验证
- [ ] [vendor/AGENTS.md](../../../AGENTS.md) 子模块路由表包含 ark-cli 条目，类型标注为 third_party
- [ ] [vendor/AGENTS.md](../../../AGENTS.md) 路由表中 ark-cli 条目说明准确
- [ ] [vendor/README.md](file:///d:/spaces/SpecWeave/vendor/README.md) 依赖清单表格包含 ark-cli 行
- [ ] [vendor/README.md](file:///d:/spaces/SpecWeave/vendor/README.md) 中 ark-cli 的版本、类型、日期、用途字段正确
- [ ] [vendor/VERSION.md](../../../playground/p-mp3vhbf2kvv431-worker5/final-learning-package/VERSION.md) 版本表格包含 ark-cli 行
- [ ] [vendor/VERSION.md](../../../playground/p-mp3vhbf2kvv431-worker5/final-learning-package/VERSION.md) 中 ark-cli 的 commit hash、来源地址、日期、许可证、类型、分支字段填写正确
- [ ] [vendor/VERSION.md](../../../playground/p-mp3vhbf2kvv431-worker5/final-learning-package/VERSION.md) 更新记录章节有 2026-07-07 引入 ark-cli 的条目
- [ ] 所有 Markdown 表格格式正确，列对齐一致，无语法错误

## Git 状态验证
- [ ] `git status` 显示 .gitmodules 为 modified（或 new file）
- [ ] `git status` 显示 vendor/ark-cli 为 new file（gitlink 模式 160000）
- [ ] `git status` 显示 vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 为 modified
- [ ] `git diff --cached --name-only` 仅列出预期文件，无意外暂存内容
- [ ] 工作区无其他意外变更（docs/knowledge 下的未跟踪文件为预期内容，与本次任务无关）
- [ ] 未执行 git commit（提交需用户确认）

## 子模块可维护性验证
- [ ] ark-cli 类型为 third_party（第三方只读），未创建 vendor/ark-cli/AGENTS.md
- [ ] 未修改 vendor/ark-cli/ 内的任何文件
- [ ] `git submodule update --init vendor/ark-cli` 命令逻辑可正常工作（其他开发者克隆后可初始化）
