# 改进建议与行动计划

## 改进建议

### P0：立即执行（本次复盘已完成）

| # | 建议 | 状态 | 说明 |
|---|------|------|------|
| 1 | 修复cli.py 6个编码边界问题 | ✅ 已完成 | _is_tty()安全封装、cp65001支持、dict.get()防御等 |
| 2 | 补充cli.py边界测试至50个 | ✅ 已完成 | 覆盖TTY检测、编码识别、symbol查找等场景 |
| 3 | 修复frontmatter.py YAML注释正则 | ✅ 已完成 | `[ \t]+#`要求空白前缀 |
| 4 | 282个测试全量验证通过 | ✅ 已完成 | 无回归 |

### P1：近期执行（下次同类任务时应用）

| # | 建议 | 优先级 | 预期收益 |
|---|------|--------|---------|
| 1 | 将`_is_tty()`模式推广到其他lib/模块 | 高 | 所有共享库模块的stream操作都应防御性访问 |
| 2 | 审查lib/下其他模块是否存在类似的直接属性访问问题 | 高 | 预防性修复，避免类似bug |
| 3 | 在共享库开发规范中增加"边界测试检查清单" | 中 | 系统化防止happy path思维 |
| 4 | 更新cross-platform-encoding-enforcement模式，补充三层防御体系 | 中 | 模式库完整性 |
| 5 | 新增defensive-attribute-access模式文档 | 中 | 可复用经验沉淀 |

### P2：中长期改进

| # | 建议 | 优先级 | 预期收益 |
|---|------|--------|---------|
| 1 | 将边界测试矩阵（5维度）做成测试模板/脚手架 | 低 | 新模块自动生成边界测试骨架 |
| 2 | 性能基准测试纳入CI流水线，在Windows/Linux/macOS多环境运行 | 低 | 环境差异导致的bug更早发现 |
| 3 | 开发stream安全访问工具装饰器/上下文管理器 | 低 | 进一步降低防御性编程的样板代码 |

## 行动计划

### 行动1：萃取defensive-attribute-access模式（本步骤执行）

**负责人**：developer（AI智能体）
**产出物**：`docs/retrospective/patterns/code-patterns/defensive-attribute-access.md`
**验收标准**：
- [ ] 包含问题现象描述
- [ ] 包含反模式示例
- [ ] 包含正确实现模板（getattr→callable→try-except三层）
- [ ] 包含适用场景清单
- [ ] 包含与其他模式的关系
- [ ] TOML frontmatter中maturity="L2"

### 行动2：更新cross-platform-encoding-enforcement模式（本步骤执行）

**负责人**：developer（AI智能体）
**产出物**：更新现有模式文档
**验收标准**：
- [ ] 补充"第二层：能力检测"章节（_is_tty + _supports_unicode）
- [ ] 补充"第三层：输出适配"章节（_symbol Unicode/ASCII双模式）
- [ ] 更新validation_count和reuse_count
- [ ] related_patterns中添加defensive-attribute-access

### 行动3：审查lib/下其他模块的防御性编程（后续执行）

**负责人**：developer
**触发条件**：下次修改.agents/scripts/lib/下任何模块时
**检查项**：
- [ ] 是否有直接调用`stream.isatty()`而无保护？
- [ ] 是否有`dict[key]`查找未验证key存在？
- [ ] 是否有`obj.attr`直接访问而未考虑attr可能不存在？
- [ ] 是否有`.lower()`/`.upper()`等方法调用未验证类型？
- [ ] 边界测试是否覆盖None/错误类型/缺失属性等场景？

## 模式萃取

### 新增模式：defensive-attribute-access

见文件创建：[defensive-attribute-access.md](../../../../patterns/code-patterns/defensive-attribute-access.md)

### 更新模式：cross-platform-encoding-enforcement

见文件更新：[cross-platform-encoding-enforcement.md](../../../../patterns/code-patterns/cross-platform-encoding-enforcement.md)

## 提交记录

本次复盘涉及的原子提交：

| Commit | 类型 | 说明 |
|--------|------|------|
| b8c6bc9 | fix(parser) | 修复YAML无引号值中#被误判为注释的问题 |
| a305234 | feat(testing) | 新增核心函数性能基准测试框架 |
| 75d24dc | chore(scripts) | 减少重复实现并防止文档生成代码污染门禁 |
| 9050aa9 | chore(merge) | 合并origin/main质量护栏更新并解决冲突 |
| f18c260 | fix(cli) | 增强输出模块鲁棒性修复Windows编码兼容性边界问题 |
| a6744b9 | docs(readme) | 补充RACI治理规范文档导航索引入口 |
