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

## 贡献规范补充

- 新增智能体角色时，需同步更新 `AGENTS.md` 角色索引表与 `.agents/roles/README.md`。
- 新增协作协议时，需同步更新 `AGENTS.md` 协作协议概要表与 `.agents/protocols/README.md`。
- 新增工作流时，需包含 Mermaid 流程图并更新 `.agents/workflows/README.md`。
- 所有 Markdown 文档使用中文撰写，技术术语保留英文原文。

> **关联模块**：
> - `README.md`
> - `docs/development-standards.md`
> - `AGENTS.md`