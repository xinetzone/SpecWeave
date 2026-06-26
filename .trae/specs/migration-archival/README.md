# migration-archival — 迁移与归档

本主题包含外部内容引入、沙箱治理、历史项目迁移、归档体系建立相关的规格文档。跨项目/跨目录的内容迁移、归档、安全治理均归入此主题。

**主题状态**：✅ 全部完成（2/2）
**上级看板**：[返回全局执行看板](../README.md)
**任务模板**：[migration-archival-task-template.md](../../../.agents/templates/theme-templates/migration-archival-task-template.md)

---

## 📊 主题执行看板

| Spec 名称 | 状态 | 完成度 | 交付物 | 简述 |
|---|---|---|---|---|
| [xinet-content-extraction-and-archiving](xinet-content-extraction-and-archiving/) | ✅ 完成 | 100% | 归档方案 | xinet 沙箱目录系统性内容萃取与归档方案，将沙箱中有价值的内容系统性提取 |
| [plan-xinet-project-migration](plan-xinet-project-migration/) | ✅ 完成 | 100% | [migration-plan.md](plan-xinet-project-migration/migration-plan.md) | xinet 沙箱多项目迁移落地计划，包含项目清单、优先级、迁移步骤、风险控制 |

---

## 🔀 主题内执行路线图

```mermaid
flowchart LR
    subgraph 第一阶段：调研萃取
        XCEA[xinet-content-extraction-and-archiving<br>✅ 完成]
    end

    subgraph 第二阶段：迁移计划
        PXPM[plan-xinet-project-migration<br>✅ 完成]
    end

    XCEA --> PXPM

    style XCEA fill:#d4edda,stroke:#28a745
    style PXPM fill:#d4edda,stroke:#28a745
```

### 执行顺序说明

1. **xinet-content-extraction-and-archiving**（最先执行）：先对源目录进行系统性调研和内容萃取，确定哪些内容值得迁移、哪些可以归档丢弃
2. **plan-xinet-project-migration**：在萃取分析基础上制定详细的迁移落地计划

---

## ⚠️ 遗留问题与跟进事项

本主题所有 spec 已 100% 完成，无待办事项。

### 迁移归档注意事项
- 迁移前务必备份源内容
- 迁移后运行路径检查脚本验证引用正确
- 归档内容标记归档日期和来源，避免后续误删
- 沙箱内容迁移前需进行安全审查（敏感信息、密钥、凭证等）

---

## 📐 主题边界与判定规则

### 归入本主题的条件
- 从项目外部（沙箱、其他项目、临时目录）引入内容到本项目
- 将项目内容归档到归档目录或清理临时内容
- 跨项目、跨仓库的内容迁移
- 沙箱环境治理（.temp/、vendor/ 等临时目录管理）
- 历史遗留内容的清理、归档、迁移
- 备份与恢复方案

### 不归入本主题的情况
- 项目内部文档结构重组（同一项目内移动） → 归入 `docs-restructure/`
- 创建新的系统或目录 → 归入 `core-foundation/`
- 编写迁移检查工具 → 归入 `standards-tools/`
- 对迁移过程复盘 → 归入 `retrospectives-insights/`

---

## 🆕 新增 Spec 指南

### 命名规范
- 使用 kebab-case，动词开头
- 常用前缀：`plan-`（迁移计划）、`migrate-`（执行迁移）、`extract-`（内容萃取）、`archive-`（归档）、`cleanup-`（清理）、`import-`（导入外部内容）
- 示例：`migrate-vendor-deps-to-pdm`、`archive-legacy-docs-2025`、`cleanup-temp-files`

### tasks.md 必备检查项

```markdown
- [ ] Task 0: 迁移前调研与准备
  - [ ] SubTask 0.1: 盘点源目录/源项目的完整文件清单
  - [ ] SubTask 0.2: 识别有价值的内容（需要迁移）、可归档内容、可删除内容
  - [ ] SubTask 0.3: 安全审查：检查是否包含敏感信息（密钥、凭证、个人数据等）
  - [ ] SubTask 0.4: 创建完整备份（迁移前可回滚）
  - [ ] SubTask 0.5: 识别所有受影响的引用路径（哪些文件引用了被迁移内容）
  - [ ] SubTask 0.6: 制定详细迁移计划（顺序、批次、每步验证点）

- [ ] Task 1: 内容萃取与清理
  - [ ] SubTask 1.1: 从源内容中萃取有价值的部分（去除噪声、临时文件）
  - [ ] SubTask 1.2: 处理敏感信息（脱敏或移除）
  - [ ] SubTask 1.3: 按目标主题/目录组织萃取后的内容
  - [ ] SubTask 1.4: 将归档内容移动到归档目录并标记元数据（来源、日期、原因）

- [ ] Task 2: 执行迁移
  - [ ] SubTask 2.1: 按计划逐批次移动/复制文件到目标位置
  - [ ] SubTask 2.2: 每批次迁移后更新相关引用路径
  - [ ] SubTask 2.3: 每批次迁移后验证内容完整性（文件数、大小校验）
  - [ ] SubTask 2.4: 跨平台路径兼容性处理（如从 Linux 迁移到 Windows）

- [ ] Task 3: 迁移后验证与收尾
  - [ ] SubTask 3.1: 运行 check-links.py 验证无死链
  - [ ] SubTask 3.2: 运行 check-move.py 验证迁移完整性
  - [ ] SubTask 3.3: 更新目标目录的 README/索引文件
  - [ ] SubTask 3.4: 验证源目录中确定删除的内容已清理
  - [ ] SubTask 3.5: 确认备份保留策略（保留多久、何时清理备份）
  - [ ] SubTask 3.6: 在本主题 README.md 中登记完成状态
```

### checklist.md 必备检查项
- 迁移前已创建完整备份
- 敏感信息已处理（脱敏或移除）
- 所有引用路径已更新（注意跨目录深度变化）
- 无死链（运行 check-links.py 验证）
- 文件数量核对（源文件数 = 迁移文件数 + 归档文件数 + 删除文件数）
- 归档文件包含元数据标记（来源、日期、归档原因）
- 临时文件和中间产物已清理
- 目标目录的索引文档（README.md）已更新包含迁移内容
- 遵循依赖管理协议（.agents/protocols/dependency-management.md）
- 不将 vendor/、.temp/、node_modules/ 等临时依赖提交到 Git

---

## 📁 目录结构

```
migration-archival/
├── README.md                                   # 本文件（主题执行看板）
├── plan-xinet-project-migration/
│   ├── spec.md
│   ├── tasks.md
│   ├── checklist.md
│   └── migration-plan.md
└── xinet-content-extraction-and-archiving/
    ├── spec.md
    ├── tasks.md
    └── checklist.md
```
