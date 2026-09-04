# Vendor 外部项目协同框架 - 验证检查清单

## 元数据完整性
- [x] vendor/VERSION.md 中 flexloop 条目包含具体 commit 哈希 d618849a（非占位符），有引入日期（2026-06-27）、许可证（Apache-2.0）、来源地址、版本标签（v0.7.1-270-gd618849）
- [x] vendor/README.md 更新了 flexloop 的用途描述（AgentForge AI Agent 协作框架参考实现）
- [x] 元数据内容准确描述了 flexloop 与 SpecWeave 的"规范-实现"关系
- [N/A] vendor/flexloop/README.md：不在 submodule 内创建元数据文件（会导致 submodule dirty），元数据统一通过 vendor/ 根级 README.md/VERSION.md 管理

## 边界划分与接口规范
- [x] 边界划分原则文档明确划分了三个区域：SpecWeave 主权区、flexloop 主权区、接口层
- [x] 边界文档包含 Mermaid 示意图（三区域边界模型图）
- [x] 接口规范覆盖四种交互方式：文档引用、脚本复用、模式参考、禁止行为
- [x] 每种交互方式有正例（正确做法）和反例（错误做法）
- [x] 禁止行为清单明确列出：不在 vendor/flexloop/ 内创建/修改文件、不直接 import vendor 内模块、不将 vendor/ 加入 sys.path、测试不遍历 vendor/

## 版本控制策略
- [x] 版本控制策略文档明确：默认固定 commit、不跟踪上游分支
- [x] 版本标识规则清晰（优先使用上游 tag，其次使用 commit 短哈希）
- [x] 更新前检查清单明确（工作树清洁、当前版本记录、无未提交变更）
- [x] 回滚机制有明确命令（git submodule update 恢复上一版本）
- [x] 兼容性评估要求（更新前查看上游 CHANGELOG）

## 子模块更新流程
- [x] 更新流程文档化为 4 步法：检查→更新→验证→提交
- [x] 每步有具体可执行的命令
- [x] 每步有明确的验证/通过标准
- [N/A] vendor-submodule-update.py 辅助脚本：未单独创建（--deep 验证脚本覆盖了验证环节，更新操作用标准 git 命令即可，避免过度封装）

## 集成验证脚本（repo-check.py vendor --deep）
- [x] 增强后的 repo-check.py vendor --deep 可正常运行
- [x] 脚本在正常状态下 exit code 为 0，所有检查项 PASS（0 错误 0 警告）
- [x] submodule 初始化检查：检测 .gitmodules 条目、目录非空、.git 文件指针（gitdir: 格式）
- [x] submodule 工作树清洁检查：通过 git status --porcelain + git submodule status 前缀检测（+/-/U 标记）
- [x] VERSION.md 一致性检查：记录的 commit 与当前 submodule HEAD 匹配
- [x] 非法引用检查：扫描 Python 文件中 sys.path.insert/append(含 vendor) 和 import vendor./from vendor.
- [x] 测试路径排除检查：验证 pytest.ini norecursedirs 包含 vendor/
- [x] 脚本输出格式清晰（沿用现有 emoji + 文本风格），错误信息包含具体说明
- [x] 脚本单次运行时间约 2.6 秒（< 10 秒要求）
- [x] 脚本遵循现有风格，使用 lib/ 共享函数，通过 repo-check.py 统一入口
- [x] 幂等性验证：连续运行两次结果一致

## dependency-management 协议更新
- [x] 协议新增"Git 子模块依赖管理"章节
- [x] 新章节覆盖：适用场景、引入流程、元数据要求、版本管理、禁止事项、克隆初始化
- [x] 验证脚本章节补充了 --deep 参数说明
- [x] 新章节与现有"手动管理依赖"章节无冲突、结构一致

## 测试环境隔离
- [x] 测试隔离规范文档说明 Python 环境隔离（主项目 .venv vs flexloop 自有 uv 环境）
- [x] pytest.ini 创建，norecursedirs 排除 vendor/.temp/.venv/.git/node_modules/.trae，testpaths 限定为 .agents/scripts/tests
- [x] 文档说明如何在需要时独立运行 flexloop 自己的测试（cd 到 vendor/flexloop 使用自有环境）
- [x] vendor 相关测试 34/34 全部通过，无回归

## 模式萃取与同步机制
- [x] 模式萃取流程包含评估→理解→适配→标注→验证→登记六个步骤
- [x] 萃取后的文件包含来源标注（source 字段或注释说明来源路径）
- [x] 回流建议明确：通过上游 PR/issue 反馈，不直接修改 submodule
- [x] 萃取流程有通用性判断标准（避免过度耦合 flexloop 特定场景的代码）

## VENDOR-INTEGRATION.md 协同指南
- [x] 文档创建在 docs/knowledge/VENDOR-INTEGRATION.md
- [x] 包含 10 个完整章节：概述、快速入门、边界划分、接口规范、版本策略、更新流程、测试隔离、模式萃取、故障排查、检查清单
- [x] 快速入门章节包含克隆后初始化命令（git submodule update --init）
- [x] 故障排查覆盖至少 3 个常见问题（submodule 未初始化、更新冲突、本地修改丢失、vendor 引用错误）
- [x] 文档中所有内部链接有效（check-links.py --path docs/knowledge/ 验证通过）
- [x] 使用 Mermaid 图表辅助说明边界模型和更新流程

## 集成与全局验证
- [x] 集成验证脚本全项 PASS（0 错误、0 警告）
- [x] 脚本幂等性验证：连续运行两次结果一致
- [x] 新脚本能力在 .agents/scripts/README.md 中有登记（--deep 参数文档）
- [x] AGENTS.md 上下文路由表更新了新文档/脚本的索引入口（vendor 条目增加 --deep 说明，新增 VENDOR-INTEGRATION.md 入口）
- [x] .trae/specs/standards-tools/README.md 看板已添加本 spec 条目并标记为完成
- [x] .gitignore 规则确认正确（vendor/* 忽略但 !vendor/flexloop/ 保留 gitlink、!vendor/README.md、!vendor/VERSION.md 白名单）
- [x] vendor/flexloop submodule 保持 clean 状态（无 modified content，无未跟踪文件）
- [x] 所有路径引用使用相对路径，无硬编码绝对路径
