---
id: "rules-alt-project-scaffold"
title: "08 模板与脚手架"
source: "alternatives-guide.md#project-scaffold"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/08-project-scaffold.toml"
---
# 08 模板与脚手架


以下为推荐的最小化项目配置骨架，展示了各替代方案的标准目录结构与关键文件。

```
project/
├── config/
│   ├── default.yaml           # 默认配置文件
│   ├── development.yaml       # 开发环境覆盖配置（可选）
│   ├── production.yaml        # 生产环境覆盖配置（可选）
│   ├── config_loader.py       # 配置加载器
│   └── __init__.py
├── constants/
│   ├── __init__.py            # 常量与枚举统一导出
│   ├── enums.py               # 枚举类型定义
│   └── patterns.py            # 正则模式常量库
├── messages/
│   ├── __init__.py            # 消息模块入口
│   └── error_messages.py      # 错误与提示消息字典
├── i18n/
│   ├── __init__.py            # 国际化模块
│   └── translator.py          # 语言加载与翻译函数
├── locales/
│   ├── zh_CN/
│   │   └── messages.py        # 简体中文语言包
│   ├── en/
│   │   └── messages.py        # 英文语言包
│   └── template.pot           # 翻译模板（可选）
├── tokens/
│   ├── design_tokens.json     # 设计令牌定义
│   └── token_loader.py        # 令牌解析器（可选）
├── .env.example               # 环境变量模板（可提交至仓库）
├── .env                       # 实际环境变量（不提交，已在 .gitignore 中）
└── .gitignore
```

**`.gitignore` 必要项**

```gitignore
# 环境变量
.env
.env.local
.env.*.local

# 运行时产物
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/
.idea/

# 操作系统
.DS_Store
Thumbs.db
```
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [07 主题变量/设计令牌](07-design-tokens.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [09 迁移策略](09-migration-strategy.md) →
