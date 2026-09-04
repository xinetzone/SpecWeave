# TOML→YAML Frontmatter 全面迁移 - Verification Checklist

## 准备阶段
- [ ] 已创建迁移专用 Git 分支
- [ ] 已创建迁移前基线 Git tag `pre-frontmatter-migration`
- [ ] 迁移前完整测试套件全部通过（282+ tests）
- [ ] 迁移前 CI 8 步检查全部通过
- [ ] 文件扫描脚本输出准确：833 个 TOML frontmatter 文件（docs:786, .agents:45, apps:1, .trae:1）
- [ ] 扫描清单包含每个文件的路径、字段列表、字段值哈希

## 转换规则与设计
- [ ] YAML 保留字段最小集已明确：id、x-toml-ref（必需）
- [ ] TOML→YAML 转义规则覆盖特殊字符（冒号、引号、#、多行值）
- [ ] TOML 数组字段转换规则已定义
- [ ] 外部 TOML 存储结构 `.meta/toml/<mirror-path>/<filename>.toml` 已确认无命名冲突
- [ ] x-toml-ref 相对路径计算规则已定义（统一使用 `/` 分隔符）
- [ ] 幂等性策略已设计（重复迁移安全）

## frontmatter.py 库更新
- [ ] `parse_frontmatter_unified()` 统一入口函数已实现
- [ ] 自动检测 YAML(`---`) / TOML(`+++`) 格式
- [ ] x-toml-ref 外部 TOML 文件加载已实现（使用 tomllib）
- [ ] YAML 字段覆盖 TOML 同名字段逻辑正确
- [ ] TOML 文件不存在/格式错误时发出 warning（非 fatal error）
- [ ] 旧 `+++` 格式解析仍正常工作（带 DeprecationWarning）
- [ ] 详细 logging 用于排查 x-toml-ref 加载问题
- [ ] 现有 API 保持向后兼容
- [ ] x-toml-ref 相关单元测试 ≥15 个，全部通过
- [ ] 测试覆盖：正常引用、路径不存在、TOML 格式错误、字段覆盖、数组、相对路径
- [ ] frontmatter.py 代码覆盖率 ≥90%
- [ ] 所有公共函数有 docstring 和类型注解

## 批量迁移脚本
- [ ] `.agents/scripts/migrate-frontmatter.py` 已创建
- [ ] `--dry-run` 模式正常工作（不修改文件）
- [ ] `--backup` 选项正常备份到 `.meta/backup/`
- [ ] `--verify` 选项正常验证一致性
- [ ] `--rollback` 选项正常从备份恢复
- [ ] 单文件转换和批量目录转换均支持
- [ ] 生成结构化 JSON 迁移报告
- [ ] Windows 路径分隔符兼容性（统一为 `/`）
- [ ] UTF-8 编码正确处理
- [ ] 迁移脚本单元测试 ≥20 个，全部通过
- [ ] 测试覆盖：dry-run、backup/rollback、幂等性、特殊字符、数组、边界情况
- [ ] 批量转换 833 文件总耗时 <30 秒
- [ ] 迁移脚本代码覆盖率 ≥90%

## 依赖脚本兼容性
- [ ] 全局搜索确认所有依赖 frontmatter 的脚本已识别
- [ ] check-source-traceability.py 已更新，兼容新格式
- [ ] check-spec-consistency.py 已更新，兼容新格式
- [ ] check-pattern-quality.py / pattern-maturity.py 已更新，兼容新格式
- [ ] docgen.py（导航/看板生成）已更新，兼容新格式
- [ ] check-agent-skills-compliance.py 已更新，兼容新格式
- [ ] check-atomization-coverage.py、check-atomization-duplication.py 已更新
- [ ] check-report-categorization.py 已更新
- [ ] generate_index.py（docs/knowledge/scripts/）已更新
- [ ] 所有依赖脚本使用统一入口 `parse_frontmatter_unified()`
- [ ] 各依赖脚本现有测试全部通过（无回归）
- [ ] 各脚本输出结果与迁移前一致

## 批量迁移执行
- [ ] 迁移脚本执行成功：成功=833，失败=0，跳过=0
- [ ] `.meta/toml/` 目录文件数 = 833
- [ ] `.meta/toml/` 目录结构与源文件镜像映射正确
- [ ] 每个外部 TOML 文件内容与原 frontmatter 完全一致
- [ ] `.meta/backup/` 备份完整（833 个文件）
- [ ] 一致性验证脚本 0 个差异（字段名+字段值完全匹配）
- [ ] 所有 Markdown 文件正文内容未被修改（仅 frontmatter 部分变更）
- [ ] YAML frontmatter 使用 `---` 包裹，语法正确
- [ ] x-toml-ref 路径使用相对路径，`/` 分隔符
- [ ] check-links.py 检查所有 x-toml-ref 路径 0 断链

## 抽样人工验证
- [ ] 随机抽取 83 个文件（10%）进行人工检查
- [ ] YAML frontmatter 格式正确（`---` 包裹、缩进正确、无语法错误）
- [ ] x-toml-ref 路径正确且可访问
- [ ] 外部 TOML 文件内容完整、与原 frontmatter 一致
- [ ] Markdown 正文内容未被修改
- [ ] 特殊字符（冒号、引号、中文、数组）正确处理
- [ ] 不同目录类型的文件（.agents/、docs/、apps/）均已验证
- [ ] 高频字段（id、source、date、type、tags 等）正确迁移

## CI 与全量测试
- [ ] pytest 完整测试套件全部通过（282+ 原有 + ≥35 新增）
- [ ] CI Step 1: 仓库合规检查通过
- [ ] CI Step 2: 链接检查通过（0 错误）
- [ ] CI Step 3: Spec 一致性检查通过
- [ ] CI Step 4: 模式成熟度检查通过
- [ ] CI Step 5: 文档生成验证通过
- [ ] CI Step 6: 重复代码检测通过（无新增重复）
- [ ] CI Step 7: 阶段守卫日志检查通过
- [ ] CI Step 8: Skill 质量检查通过（平均分 ≥90）
- [ ] 硬编码检查（check-hardcode.py）无新增误报
- [ ] RACI 合规检查 100 分
- [ ] 编码检查（verify-encoding.ps1）100% 健康分数
- [ ] 迁移前后 CI 警告数量对比：无新增警告

## 回滚机制
- [ ] `--rollback` 选项正常工作
- [ ] 回滚后所有文件恢复到迁移前状态
- [ ] 回滚后 Git 工作区清洁
- [ ] 回滚后可重新执行迁移
- [ ] Git tag `pre-frontmatter-migration` 存在且正确

## 文档更新
- [ ] `.meta/README.md` 已创建，内容清晰说明目录结构和用途
- [ ] `.gitignore` 已添加 `.meta/backup/`
- [ ] `.agents/docs/development-standards.md` frontmatter 章节已更新
- [ ] YAML(`---`) 为唯一标准格式的规范已记录
- [ ] x-toml-ref 字段使用规范已记录（含示例）
- [ ] 外部 TOML 文件存储约定已记录
- [ ] 从旧 `+++` 格式迁移指南已记录（可选）
- [ ] 所有新文档链接 check-links 验证通过（0 错误）

## 原子提交
- [ ] 提交1：`feat(scripts): add x-toml-ref support to frontmatter.py`（库+测试）
- [ ] 提交2：`feat(scripts): add migrate-frontmatter.py batch migration tool`（脚本+测试）
- [ ] 提交3：`fix(scripts): update dependent scripts for unified frontmatter parsing`（依赖更新）
- [ ] 提交4：`refactor(docs): migrate 833 TOML frontmatter files to YAML with x-toml-ref`（批量转换）
- [ ] 提交5：`docs(meta): add .meta directory README and update frontmatter standards`（文档）
- [ ] 每个提交遵循 Conventional Commits 规范（中文描述）
- [ ] 每个提交单一职责
- [ ] 无敏感信息或临时文件被提交
- [ ] 迁移统计报告已生成（文件变更数、新增数、行数变化）

## 复盘报告
- [ ] 复盘报告目录已创建：`docs/retrospective/reports/project-governance/tools-and-automation/retrospective-frontmatter-migration-20260701/`
- [ ] README.md 包含概述、关键数据、结论
- [ ] execution-retrospective.md 包含执行过程、决策记录、摩擦点
- [ ] insight-extraction.md 包含关键洞察和根因分析
- [ ] export-suggestions.md 包含后续改进建议
- [ ] 复盘文档链接和索引已更新（check-links 通过）
- [ ] 如有可复用模式，已注册到模式库并更新索引

## 最终验收
- [ ] 项目中无遗留的 `+++` TOML frontmatter（除备份和历史文档外）
- [ ] 所有 833 个文件均使用 `---` YAML frontmatter + x-toml-ref
- [ ] `.meta/toml/` 下 833 个外部 TOML 文件全部正确
- [ ] 所有测试通过、CI 通过、链接检查通过
- [ ] 文档更新完整、规范清晰
- [ ] 回滚机制验证有效
- [ ] 迁移复盘报告完成
