# fabric 知识束生成任务指导书

## 任务概述
为 fabric v4.0.0 生成符合 OKF v0.2 规范的系统化中文 Wiki 教程，遵循 R→I→E→V 四阶段工作流。

## 路径
- **源码路径**: `d:\spaces\SpecWeave\external\libs\fabric\fabric\`
- **输出路径**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\fabric\`
- **事实清单**: `d:\spaces\SpecWeave\.trae\specs\ssh-python-okf-wiki\fabric-facts.md`
- **洞察文件**: `d:\spaces\SpecWeave\.trae\specs\ssh-python-okf-wiki\fabric-insights.md`
- **格式范例**: 先读 `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\paramiko\` 了解格式（同批次生成的范例），也可读 `bundles\tooling\pyinvoke\` 了解 invoke 基础

## 版本信息
- fabric 4.0.0, commit ded51893f02c
- 基于 paramiko（SSH 底层）+ invoke（任务执行框架）
- 核心模块：connection.py, config.py, group.py, runners.py, transfer.py, tunnels.py, executor.py, tasks.py, auth.py, main.py, exceptions.py, util.py, testing/

## 关键架构关系
- `Connection` 继承 `invoke.Context`，内部组合 `paramiko.SSHClient`
- `Config` 继承 `invoke.Config`，增加 SSH 相关配置
- `Remote` 继承 `invoke.Runner`，通过 paramiko Channel 执行远程命令
- `Group`/`SerialGroup`/`ThreadingGroup` 管理多主机并行执行
- `Transfer` 封装 SFTP 文件传输
- `Tunnel`/`TunnelManager` 实现 SSH 跳板机端口转发
- fabric 与 paramiko 和 invoke（pyinvoke 知识束）有强关联，需交叉引用

## R 阶段（事实采集，50+ 事实）
阅读以下模块提取编号事实（F-001~F-050+）：
- `__init__.py` — 公开 API 导出
- `connection.py` — Connection 类（核心，最大文件）：__init__、open、close、run、sudo、local、get、put、forward_local、forward_remote、create_sftp_conn、open_gateway
- `config.py` — Config 类：SSH 配置层级、ssh_config、runtime_ssh_path
- `group.py` — Group、SerialGroup、ThreadingGroup、GroupResult：并行执行、结果收集
- `runners.py` — Remote runner：继承 invoke.Runner、start/wait/returncode、PTY
- `transfer.py` — Transfer 类：get/put 文件传输
- `tunnels.py` — Tunnel、TunnelManager：跳板机端口转发
- `executor.py` — Executor：任务执行器，按主机分组执行
- `tasks.py` — ConnectionCall：带主机参数的任务调用
- `auth.py` — 认证相关
- `main.py` — CLI 入口，Program 配置
- `exceptions.py` — 异常体系
- `testing/` — MockRemote、MockSFTP、Session 测试工具

事实格式：`F-001: [模块名] 类名/方法名(参数) — 客观描述`
**禁止**"用于"/"目的是"/"设计为"等推断词。

## I 阶段（架构洞察，3-5 个）
每个洞察含四元组：陈述+证据(源码引用)+反常识+行动

建议洞察方向：
1. Connection 的双层继承架构（is-a invoke.Context + has-a paramiko.SSHClient）
2. Group 的串行/线程并行执行模型与 GroupResult 结果聚合
3. Remote Runner 的模板方法模式（继承 invoke.Runner 并实现 start/wait）
4. Config 多层级合并与 SSH config 文件集成
5. Tunnel 跳板机的网关连接模式

## E 阶段（批量生成）

### Step 1: 创建目录
```
bundles/networking/fabric/{concepts,examples,references}/
```

### Step 2: 先生成 references/fabric-source.md
- 版本 4.0.0、源码路径、核心模块清单、公开 API、与 paramiko/invoke 的依赖关系

### Step 3: 分批生成 concepts/（≥8篇，每批≤7）

**批次1（6篇）**:
1. `00-introduction.md` — fabric 简介、v4 架构（基于 invoke+paramiko）、安装、与 fabric v1 区别
2. `01-getting-started.md` — 第一个 fab 任务、Connection 基本用法
3. `02-connection.md` — Connection 详解：host/user/port/connect_kwargs、open/close、SSH config 集成、gateway 跳板机
4. `03-configuration.md` — Config 层级、SSH config 文件、env 变量、fab 命令行选项
5. `04-command-execution.md` — run/sudo/local、Result 对象、PTY、warn/hide/echo、环境变量
6. `05-group-parallel.md` — Group/SerialGroup/ThreadingGroup、GroupResult、多主机并行

**批次2（3篇）**:
7. `06-file-transfer.md` — Transfer、get/put、SFTP 封装
8. `07-tunnels.md` — Tunnel/TunnelManager、forward_local/forward_remote、跳板机
9. `08-advanced-patterns.md` — Executor 按主机分组、ConnectionCall、测试 MockRemote、自定义 Runner

### Step 4: 生成 examples/（4篇）
1. `basic-deploy.md` — 基础部署脚本
2. `multi-server-group.md` — 多服务器组并行操作
3. `file-upload-download.md` — 文件上传下载
4. `tunnel-bastion.md` — 跳板机隧道

### Step 5: 最后生成 index.md 文件
- concepts/index.md, examples/index.md, references/index.md（无 frontmatter）
- 根 index.md（带 okf_version: "0.2"）
- log.md

## Frontmatter
同 paramiko 格式：
```yaml
type: Concept  # 或 Example、Reference
title: <标题>
description: <30-80字>
tags: [fabric, <标签>]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
```

## 交叉引用
- 引用 paramiko 知识束：`/concepts/02-ssh-client.md`（bundle-relative，注意 fabric 引用 paramiko 需要用相对路径回退：`../../paramiko/concepts/02-ssh-client.md`）
  - **重要**：跨 bundle 链接不能用 `/` 开头（那是 bundle-relative），需用相对路径 `../../paramiko/concepts/02-ssh-client.md`
- 引用 pyinvoke 知识束：`../../tooling/pyinvoke/concepts/03-context-object.md`
- 文档结尾"相关概念"章节包含这些跨束链接

## V 阶段（Grep 验证，必须执行）
在 `external/libs/fabric/fabric/` 中 Grep 验证：
- 类名: Connection, Config, Group, SerialGroup, ThreadingGroup, GroupResult, Remote, Transfer, Tunnel, TunnelManager, Executor, ConnectionCall, Config
- 方法: run, sudo, local, get, put, open, close, forward_local, forward_remote, create_sftp_conn, open_gateway, from_context
- 测试工具: MockRemote, MockSFTP, Session

验证失败的必须修正为真实 API。

## 返回
事实总数、文件列表、虚构 API 修复记录、Grep 验证结果摘要。
