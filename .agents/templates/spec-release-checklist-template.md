---
id: "spec-release-checklist-template"
title: "规范发布Checklist模板"
source: "insight-extraction.md#规范悬空三缺原则"
x-toml-ref: "../../.meta/toml/.agents/templates/spec-release-checklist-template.toml"
---
# 规范发布Checklist模板

> 基于 **规范三同步原则**（spec-triple-sync）：新规范发布必须完成"发现→导航→示范"三项同步，否则规范必然悬空。

## 使用方法

1. 复制本模板内容
2. 将 `{规范名称}`、`{规范路径}` 等占位符替换为实际值
3. 在规范发布过程中逐项打勾
4. 所有项目勾选完成后方可原子提交

---

## 📋 规范发布Checklist

### 一、规范内容编写（20%工作量）

```
规范名称: {规范名称}
规范路径: .agents/rules/{rule-file-name}.md
规范类型: {rules/standards/protocols/templates/workflows}
```

- [ ] **规范正文完整**：规范文档已编写，包含目的、适用范围、核心规则、正反示例、验证方式
- [ ] **frontmatter合规**：id/title/source/x-toml-ref四字段完整，遵循 [frontmatter-metadata-standard](../rules/frontmatter-metadata-standard.md)
- [ ] **4字段frontmatter**：id为kebab-case，source标注来源，x-toml-ref路径正确
- [ ] **正反示例齐全**：每个规则点包含"禁止写法 ❌"和"正确写法 ✅"对照
- [ ] **可验证**：提供明确的验证命令或检查方式（脚本/人工检查步骤）

### 二、发现同步（让大家知道规范存在）

- [ ] **总览入口引用**：在 [.agents/README.md](../../README.md) 核心规范入口表中添加一行
  - 位置："核心规范入口"表格
  - 格式：`| 📏 规范分类 | [规范名称](rules/{file}.md) | 一句话说明 |`
- [ ] **规则索引更新**：在 [.agents/rules/README.md](../rules/) 对应分类中添加链接
- [ ] **角色定义引用**：如规范适用于特定角色，在 `.agents/roles/{role}.md` 的"遵循规则"部分添加引用
- [ ] **AGENTS.md路由**：如果是高频/核心规范，在 [AGENTS.md](../../AGENTS.md) 上下文路由表中添加入口

### 三、导航同步（执行时能找到规范）

- [ ] **上下文路由表更新**：在 [.agents/context-routing.md](../context-routing.md) 中添加任务类型→规范的映射
  - 明确"遇到X类任务时必读Y规范"
- [ ] **跨文档链接**：在相关开发规范文档中添加指向新规范的链接
  - 如：[docs/development-standards.md](../../docs/development-standards.md) 中对应章节
- [ ] **相关协议引用**：如规范涉及协作流程，在 `.agents/protocols/` 对应协议中补充引用
- [ ] **工作流集成**：如规范涉及标准操作流程，在 `.agents/workflows/` 中更新对应工作流步骤

### 四、示范同步（看到规范就知道怎么做）

- [ ] **存量迁移示范**：至少选择1个存量文件/目录作为示范案例完成迁移
  - 示范文件路径：`{示范文件路径}`
  - 提交记录：`{commit hash}`
- [ ] **代码示例正确**：规范中的代码示例已在真实文件中验证可运行
- [ ] **自动化工具就绪**：如规范涉及机械重复操作，配套脚本/工具已就绪
  - 工具路径：`.agents/scripts/{tool-name}.py`（如适用）
  - 工具已测试通过
- [ ] **常见错误覆盖**：规范的"常见错误与修复"章节已覆盖迁移过程中遇到的典型错误

### 五、提交前验证

- [ ] **链接检查通过**：`python .agents/scripts/check-links.py --path .agents/rules/`
- [ ] **frontmatter校验通过**：`python .agents/scripts/check-frontmatter.py --dir .agents/rules/`
- [ ] **原子提交**：提交信息遵循Conventional Commits格式
  - 建议type：`docs(rules)` 或 `refactor(rules)`
  - 提交范围单一，不混入无关变更

---

## 快速自检表（三同步原则速查）

| 同步项 | 检查问题 | 通过标准 |
|--------|---------|---------|
| 🔍 **发现** | "团队中一个不知道这个规范存在的人，能在哪里看到它？" | 总览README中有入口链接 |
| 🧭 **导航** | "正在执行相关任务的人，能通过路由表找到这个规范吗？" | context-routing.md中有映射 |
| 🎯 **示范** | "第一次看到规范的人，能找到一个真实的正确示例吗？" | 至少1个存量文件已完成迁移示范 |

---

## 参考模式

本Checklist基于以下可复用模式：
- [spec-triple-sync](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md) — 规范三同步原则
