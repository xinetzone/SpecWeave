---
id: "okf-wiki-quickstart"
title: "02 5分钟快速入门"
version: "1.0"
source: "okf.md quickstart改编为AI Agent场景"
type: "Wiki Tutorial"
description: "零依赖5分钟创建你的第一个OKF Bundle：Agent工具知识库完整实操示例"
tags: ["OKF", "Quickstart", "快速上手", "实操", "零依赖"]
category: "learning"
date: "2026-08-05"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "OKF零安装零依赖，6个步骤创建一个Agent工具知识库Bundle（3个工具Concept+index+log），5分钟完成并通过三规则验证"
last_verified: "2026-08-05"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/02-quickstart.toml"
---

# 02 5分钟快速入门

OKF不需要安装任何软件、SDK、数据库，只需要文本编辑器和终端（可选）。`cat`能读，`git`能管，OKF就能工作。

## 2.1 什么是Bundle（10秒解释）

- 一个装`.md`文件的文件夹
- 每个文件是一个**Concept**（概念）
- 每个Concept有YAML frontmatter，至少有`type`字段
- 就这么简单

## 2.2 最终目录结构

我们将构建一个`agent-tools-kb/`（Agent工具知识库），结构如下：

```
agent-tools-kb/
├── index.md      ← 列出Bundle内容（目录）
├── log.md        ← 变更历史
├── bash.md       ← Concept: Bash命令执行工具
├── browser.md    ← Concept: 浏览器自动化工具
└── file-read.md  ← Concept: 文件读取工具
```

扁平结构，不需要子目录。小Bundle保持简单即可。

### Step 1: 创建目录

```bash
mkdir agent-tools-kb && cd agent-tools-kb
```

### Step 2: 第一个Concept - Bash工具

创建`bash.md`：

```markdown
---
type: Tool
title: Bash命令执行工具
description: 执行shell命令，进行系统操作、脚本运行、文件管理
tags: [shell, terminal, system, command]
---

# Bash命令执行工具

## Description
在沙箱环境中执行shell命令，支持文件操作、脚本运行、系统调用。是Agent与操作系统交互的核心工具。

## Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| command | string | 是 | 要执行的shell命令 |
| cwd | string | 否 | 工作目录，默认为Bundle根目录 |

## Examples
```bash
ls -la
python script.py
cat config.json
```

## When to use
- 创建/修改/删除文件时
- 运行构建命令、测试脚本时
- 执行git等版本控制操作时

## Notes
- 命令在沙箱中执行，有文件系统权限限制
- 大文件读取请使用 [文件读取工具](./file-read.md)
- 网页交互请使用 [浏览器自动化工具](./browser.md)
```

### Step 3: 第二个Concept - 浏览器工具

创建`browser.md`：

```markdown
---
type: Tool
title: 浏览器自动化工具
description: 网页导航、元素交互、截图、数据提取、表单填写
tags: [web, browser, automation, playwright]
---

# 浏览器自动化工具

## Description
通过Chrome DevTools Protocol控制浏览器，支持导航、点击、输入、截图、内容提取。用于网页交互和Web应用测试。

## Capabilities
- **导航**: 打开URL、前进后退、刷新
- **交互**: 点击、填写表单、键盘输入、滚动
- **提取**: 获取页面文本、属性、HTML内容
- **媒体**: 页面截图、PDF导出

## Examples
```
导航到 https://example.com
点击 #login-button
输入用户名/密码
等待加载完成
截图保存为 result.png
```

## When to use
- 需要登录网站获取认证内容时
- 与JavaScript渲染页面交互时
- 自动化表单提交流程时
- 提取动态加载数据时

## Notes
- 下载文件后，使用 [文件读取工具](./file-read.md) 读取
- 批量静态抓取可配合curl通过 [Bash工具](./bash.md) 执行
- 默认使用无头模式
```

### Step 4: 第三个Concept - 文件读取工具

创建`file-read.md`：

```markdown
---
type: Tool
title: 文件读取工具
description: 安全读取本地文件内容，支持文本、代码、配置文件
tags: [file, io, read, filesystem]
---

# 文件读取工具

## Description
安全读取本地文件系统中的文件，支持大文件分段读取、行号偏移、多种编码。是Agent访问本地知识的主要入口。

## Parameters
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_path | string | 是 | 文件绝对路径 |
| offset | number | 否 | 起始行号，默认1 |
| limit | number | 否 | 读取行数，默认2000 |

## Supported Formats
- **文本**: .md, .txt, .json, .yaml, .toml, .csv
- **代码**: .py, .js, .ts, .go, .rs, .java
- **配置**: .ini, .cfg, .env

## When to use
- 读取代码文件进行分析/修改时
- 读取OKF Bundle中的Concept文件时
- 查看配置文件、日志内容时
- 读取下载的数据文件时

## Restrictions
- 默认读取上限2000行，大文件需分段
- 二进制文件仅返回元数据
- 沙箱外路径受权限限制

## Notes
- 需要修改文件时，配合 [Bash工具](./bash.md) 使用Edit/Write
- 使用Glob先定位路径，避免猜测
- 大文件用offset/limit分段，避免token溢出
```

### Step 5: 创建index.md

index.md**没有frontmatter**，直接是内容：

```markdown
# Agent工具知识库

这个Bundle描述了AI Agent常用的三个核心工具。

## 核心工具
* [Bash命令执行](./bash.md) - 执行shell命令，系统操作和脚本运行
* [浏览器自动化](./browser.md) - 网页导航、交互、截图、数据提取
* [文件读取](./file-read.md) - 读取本地文件内容，支持多种格式
```

index是Bundle的目录表，人和Agent都从这里开始浏览。

### Step 6: 创建log.md

log.md也没有frontmatter，按ISO日期倒序记录变更：

```markdown
# Bundle更新日志

## 2026-08-05
* **创建**: 初始Bundle，包含三个核心Agent工具
* **创建**: 添加[Bash工具](./bash.md)文档与示例
* **创建**: 添加[浏览器工具](./browser.md)文档与注意事项
* **创建**: 添加[文件读取工具](./file-read.md)文档与最佳实践
```

## 2.3 快速验证：三规则检查清单

你的Bundle符合OKF v0.2规范，如果：

1. ✅ 所有不是index.md/log.md的`.md`文件都有可解析的YAML frontmatter
2. ✅ 每个frontmatter都有`type`字段且有值
3. ✅ index.md和log.md遵循规范（无frontmatter，分别是目录和按日期的变更日志）

就这三条检查。title/description/tags是推荐字段，不影响合规性。

官方验证器：https://okf.md/validator （浏览器中上传或粘贴验证，零后端零安装）

## 2.4 你刚刚构建了什么

一个可导航的知识图谱：

- Agent通过`index.md`列出所有概念
- Agent通过`type`字段理解概念类型，路由到正确处理方式
- Agent通过交叉链接导航概念间关系
- 人和Agent通过`log.md`查看知识演进历史

不需要数据库、API、厂商锁定，知识像Git仓库一样可移植。

## 2.5 下一步建议

- Bundle变大时添加子目录（`tools/`、`concepts/`、`playbooks/`）
- 当工具对应真实API时，在frontmatter加`resource:`字段
- 用Git做版本控制，每次commit都是知识状态的快照
- 添加`owner:`、`confidence:`、`stale_after:`等扩展元数据
- 运行官方validator验证合规性
- 尝试让Agent读取你的Bundle回答问题

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [01 核心概念与设计哲学](./01-core-concepts.md) | [README](./README.md) | [03 使用模式与最佳实践](./03-usage-patterns.md) |
