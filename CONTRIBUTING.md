# 贡献指南

> **来源**：从 `README.md` "贡献指南"章节拆分

欢迎为本规范体系贡献内容！请遵循以下流程：

## 1. 准备工作

```bash
# Fork 仓库后克隆到本地
git clone <your-fork-url>
cd <repository-name>

# 确认验证脚本通过
python .agents/scripts/check-gitignore.py
```

## 2. 创建分支

```bash
git checkout -b feat/your-feature
```

分支命名遵循 `type/brief-description` 格式，例如 `feat/add-new-role`、`fix/handoff-protocol`。

## 3. 提交变更

- 遵循 [Conventional Commits](https://conventionalcommits.org) 规范。
- 每个提交应是逻辑完整的原子单元，聚焦单一职责。
- 提交信息主体使用中文描述。

```bash
git add <相关文件>
git commit -m "feat: 添加 XXX 角色" -m "详细说明变更原因与影响。"
```

## 4. 提交前检查

- [ ] 验证脚本通过：`python .agents/scripts/check-gitignore.py`
- [ ] 链接校验通过：`python .agents/scripts/check-links.py --path <变更目录>`（确保无 `file:///` 绝对路径断链）
- [ ] 提交信息符合 Conventional Commits 规范
- [ ] 变更不包含临时依赖（`vendor/`、`.temp/` 等）
- [ ] 新增角色/协议/工作流已更新对应 README.md 索引

## 5. 发起 Pull Request

- PR 标题遵循 Conventional Commits 格式。
- PR 描述说明：变更内容、变更原因、影响范围、验证方式。
- 等待代码审查（由 `reviewer` 角色或维护者执行）。

## 6. 🚀 首次贡献指南（Good First Issue）

> **如果你是第一次贡献开源项目，或者第一次接触 SpecWeave，请从这里开始！**
>
> 我们承诺：每个 Good First Issue 都有维护者提供一对一指导，你的第一个PR **一定会**被认真对待。

### 什么是 Good First Issue？

Good First Issue 是专门为新贡献者准备的入门任务，满足以下条件：

- ✅ **修改范围小**：通常只需修改 1-2 个文件，代码/文档改动 ≤20 行
- ✅ **边界清晰**：任务描述明确告诉你要做什么、改哪里、怎么验证
- ✅ **不需要深入理解整个项目**：只需了解被修改的那一小块内容
- ✅ **有维护者背书**：每个GFI都有指定的指导人（mentor），可以@他们提问

### 永远存在的微任务（不需要等Issue）

以下任务随时可以做，不需要先开Issue讨论，直接提交PR即可：

| 任务类型 | 具体示例 | 修改位置 | 预计耗时 |
|---------|---------|---------|---------|
| **修复错别字** | 文档中的错字、语法错误、标点问题 | `.agents/docs/` 下任意 `.md` 文件 | 5-10分钟 |
| **修复断链** | Markdown中引用的相对路径404 | 包含错误链接的 `.md` 文件 | 10-15分钟 |
| **补充注释** | Python脚本中难以理解的函数缺少docstring | `.agents/scripts/` 下的 `.py` 文件 | 10-20分钟 |
| **改进翻译** | 中英文术语翻译不统一、表达不自然 | 任意 `.md` 文件 | 10-20分钟 |
| **添加测试用例** | 为现有函数补充边界情况测试 | `.agents/scripts/tests/` | 20-30分钟 |
| **报告Bug** | 使用中遇到的问题，详细记录复现步骤 | GitHub Issues | 10分钟 |

> 💡 **微任务PR提交方式**：直接Fork→修改→提交PR，标题使用 `docs: fix typo in xxx` 或 `fix: correct link to xxx` 格式即可。无需事先讨论。

### 如何找到标记的 Good First Issue？

1. 访问 [Issues页面](https://github.com/xinetzone/SpecWeave/issues)
2. 筛选标签 `good first issue`
3. 选择一个你感兴趣的Issue，在下面评论：*"我想尝试这个问题！"*
4. 维护者会在24小时内回复确认，并@指导人为你提供帮助

### Good First Issue 工作流

```
步骤1：在Issue下评论"我想尝试" → 步骤2：维护者确认并指派给你
→ 步骤3：按本指南第1-5步操作（Fork→分支→修改→检查→PR）
→ 步骤4：PR中 @ 指导人请求审查
→ 步骤5：根据反馈修改（可能需要1-3轮）
→ 步骤6：合入！🎉
```

### 首次贡献者承诺

我们对首次贡献者做出以下承诺：

- 🟢 **不会因为"不完美"而拒绝**：只要方向正确，格式/细节问题维护者会帮你修正，不会让你反复修改
- 🟢 **48小时内回复**：你的PR评论和问题会在48小时内得到回复（节假日除外）
- 🟢 **零责备文化**：犯错是正常的，不会有人因为你写错了什么而批评你
- 🟢 **贡献者墙署名**：首次PR合入后，你的名字会被加入贡献者列表（CONTRIBUTORS.md）

### 第一次贡献？这里有一个示例路径

如果你完全不知道从哪里开始，按这个路径走：

1. **5分钟阅读**：[AGENTS.md](AGENTS.md) 前100行，了解项目是什么
2. **10分钟探索**：浏览 [.agents/docs/](.agents/docs/) 目录，看看哪个文档你最容易理解
3. **5分钟寻找**：在那个文档里找一个错别字或不通顺的句子
4. **15分钟操作**：按本指南第1-5步，Fork→修改→提交PR
5. **等待合入**：你已经是贡献者了！🎊

> **不确定怎么做？** 直接在Issue中提问，或者在PR中写"这是我的第一次贡献，请帮我看看有没有问题"——我们会非常乐意帮助你。

## 贡献规范补充

- 新增智能体角色时，需同步更新 `AGENTS.md` 角色索引表与 `.agents/roles/README.md`。
- 新增协作协议时，需同步更新 `AGENTS.md` 协作协议概要表与 `.agents/protocols/README.md`。
- 新增工作流时，需包含 Mermaid 流程图并更新 `.agents/workflows/README.md`。
- 所有 Markdown 文档使用中文撰写，技术术语保留英文原文。

> **关联模块**：
> - `README.md`
> - `MAINTAINERS.md` — 维护者清单与职责
> - `BUSFACTOR.md` — 紧急接续维护手册
> - `.agents/docs/development-standards.md`
> - `AGENTS.md`