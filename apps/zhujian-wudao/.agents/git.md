# .agents/git.md — Git 版本管理规范

本项目采用[约定式提交](https://www.conventionalcommits.org/zh-hans/)规范管理 Git 提交信息。

## 提交格式

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

描述使用中文、现在时、祈使语气，首行不超过 72 字符。

## 提交类型与作用域

| 类型 | 含义 | 项目中的典型场景 |
|------|------|----------------|
| `docs` | 文档变更 | 新增/修改洞察、更新 spec、修改报名帖 |
| `feat` | 新功能 | HTML 原型新增交互能力 |
| `fix` | 缺陷修复 | 修复 HTML 原型 bug、修正文档不一致 |
| `refactor` | 重构 | 重写 HTML 代码结构、调整文档组织 |
| `style` | 格式调整 | 代码缩进、标点修正（不改变逻辑） |
| `chore` | 杂项维护 | 更新 .gitignore、调整项目配置 |

| 作用域 | 对应范围 |
|--------|---------|
| `spec` | `.agents/docs/superpowers/specs/` 规格文档 |
| `insights` | 洞察库文件 |
| `html` | `竹简悟道.html` 原型 |
| `agents` | `.agents/` 及 `AGENTS.md` |
| `review` | 复盘报告 |

## 示例

```bash
git commit -m "docs(insights): 新增洞察54 虚室生白"
git commit -m "feat(html): 实现体道四法交互展合组件"
git commit -m "fix(html): 修正场景标签与 spec 不一致的问题"
```

## 破坏性变更

```bash
# 感叹号标记
git commit -m "refactor(html)!: 重构体道链数据结构为嵌套格式"

# 脚注声明
git commit -m "refactor(html): 重构体道链数据结构

BREAKING CHANGE: 体道链从线性数组改为嵌套树结构"
```

## 提交粒度

每次提交只包含一个逻辑变更，禁止将无关改动打包提交（如"新增洞察 + 修改 HTML 样式"应拆分为两次提交）。
