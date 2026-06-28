+++
id = "dry-run-first"
domain = "methodology"
layer = "methodology"
maturity = "L3"
validation_count = 3
reuse_count = 2
documentation_level = "standard"
source = "docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insight-extraction.md"

[bindings]
rules = []
references = []
skills = []
+++

# dry-run 优先的安全修改模式（dry-run-first）

## 模式类型
方法论模式

## 成熟度
L3 标准化（多次验证，多个工具复用此模式）

## 适用场景
任何批量修改文件的自动化工具（链接修复、代码重构、批量重命名、配置更新、数据库迁移等）

## 问题背景
自动化批量修改工具若直接执行写入操作，一旦算法有误可能导致大规模文件损坏，且难以回滚。用户对"黑盒修改"天然不信任。

## 标准实现步骤

```mermaid
flowchart LR
    A["默认 dry-run 模式"] --> B["输出变更清单<br/>文件位置+原值→新值"]
    B --> C{"用户确认?"}
    C -->|"否"| D["取消操作"]
    C -->|"是"| E["执行实际写入"]
    E --> F["立即运行验证<br/>确认修复效果"]
```

### 步骤 1：默认 dry-run
- 默认运行在 dry-run 模式（或需要明确 flag 如 `--apply`/`--fix` 才执行写入）
- 不提供"直接修改"作为默认行为

### 步骤 2：清晰输出变更清单
dry-run 输出必须包含：
- 将要修改的文件路径
- 原值（before）
- 新值（after）
- 修改原因/使用的策略
- 统计汇总（修改文件数、跳过文件数、无法处理数）

### 步骤 3：用户确认
- 用户看到预览后，通过 flag 或交互确认执行实际写入
- 非交互环境下要求明确 flag，禁止隐式确认

### 步骤 4：写入后立即验证
- 实际写入后立即运行验证逻辑
- 确认修复达到预期效果
- 报告验证结果

## 关键要点

1. **预览即文档**：dry-run 输出本身就是最好的用户文档，用户通过预览理解工具行为
2. **零副作用**：dry-run 模式绝不能修改任何文件
3. **信任建立**：用户通过多次 dry-run→确认→验证的循环建立对工具的信任
4. **开发者自测**：dry-run 也是开发者验证算法正确性的重要手段

## 成功案例

| 工具 | dry-run 实现 | 验证结果 |
|------|-------------|---------|
| check-links.py --fix | `--fix --dry-run` 输出修复计划 | ✅ 全量链接正确状态下输出"未发现需要修复的断链" |
| finalize-atomization.py | 默认dry-run，需 `--apply` 执行 | ✅ 原子化后处理验证通过 |
| 数据库迁移工具 | 标准迁移模式：plan → apply → verify | 行业最佳实践 |

> **关联模块**：
> - `fix-priority-chain.md` — 修复优先级链（精确优先策略配合dry-run）
> - `relative-depth-adjustment.md` — 相对路径深度校正算法
