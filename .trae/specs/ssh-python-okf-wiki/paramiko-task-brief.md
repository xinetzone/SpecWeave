# paramiko 知识束生成任务指导书

## 任务概述
为 paramiko v5.0.0 生成符合 OKF v0.2 规范的系统化中文 Wiki 教程，遵循 R→I→E→V→C 五阶段工作流。

## 路径
- **源码路径**: `d:\spaces\SpecWeave\external\libs\paramiko\paramiko\`
- **输出路径**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\paramiko\`
- **事实清单**: `d:\spaces\SpecWeave\.trae\specs\ssh-python-okf-wiki\paramiko-facts.md`
- **洞察文件**: `d:\spaces\SpecWeave\.trae\specs\ssh-python-okf-wiki\paramiko-insights.md`
- **参考范例**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\tooling\pyinvoke\`（完整的 OKF 知识束范例，必读其 index.md、concepts/00-introduction.md、references/pyinvoke-source.md 了解格式）

## 版本信息
- paramiko 5.0.0, commit d60d5c17d78f
- 纯 Python SSH2 协议库，依赖 cryptography、bcrypt、pynacl

## R 阶段（事实采集）
深度阅读以下核心模块，提取 60+ 编号事实：
- `__init__.py` — 公开 API 导出
- `client.py` — SSHClient 高层接口
- `transport.py` — Transport 底层传输（核心，最大文件）
- `channel.py` — Channel 通道
- `auth_handler.py` — 认证处理
- `auth_strategy.py` — 认证策略
- `pkey.py` — 密钥基类
- `rsakey.py`, `ed25519key.py`, `ecdsakey.py` — 具体密钥类型
- `sftp_client.py` — SFTPClient
- `sftp.py`, `sftp_file.py`, `sftp_attr.py`, `sftp_handle.py`, `sftp_server.py`, `sftp_si.py` — SFTP 子系统
- `server.py` — ServerInterface 服务端
- `hostkeys.py` — HostKeys 主机密钥管理
- `agent.py` — SSH Agent 客户端
- `proxy.py` — ProxyCommand
- `common.py` — 通用工具（MTValue 等）
- `message.py` — SSH 消息
- `packet.py` — 数据包处理
- `buffered_pipe.py` — 缓冲管道
- `file.py` — 文件对象
- `config.py` — SSH config 解析
- `compress.py` — 压缩
- `kex_*.py` — 密钥交换算法
- `ssh_exception.py` — 异常体系
- `util.py` — 工具函数

事实格式：`F-001: [模块名] 类名/方法名(参数) — 客观描述，指向源码文件`
**禁止**出现"用于"/"目的是"/"设计为"等推断词。

## I 阶段（架构洞察）
提炼 3-5 个核心洞察，每个包含四元组：
- **陈述**: 架构事实
- **证据**: 具体源码引用（文件:类/方法）
- **反常识**: 与直觉相反的设计决策
- **行动**: 对文档生成的指导

设计知识地图：入门(2篇) → 核心(5篇) → 高级(4篇)，共 11 篇概念文档。

## E 阶段（批量生成，严格遵守顺序）

### Step 1: 创建目录结构
```
bundles/networking/paramiko/
├── concepts/
├── examples/
└── references/
```

### Step 2: 先生成 references/paramiko-source.md（信源先行！）
记录：版本、源码路径、核心模块清单表、公开 API 导出列表、CLI 入口点。
sources 字段指向 GitHub: https://github.com/paramiko/paramiko

### Step 3: 分批生成 concepts/（每批 ≤7 篇）

**批次1（入门+核心，7篇）**:
1. `00-introduction.md` — paramiko 简介、设计哲学、安装、与其他 SSH 库对比
2. `01-getting-started.md` — 5分钟快速上手、第一个 SSH 连接
3. `02-ssh-client.md` — SSHClient 详解：connect/exec_command/invoke_shell/open_sftp/set_missing_host_key_policy
4. `03-transport.md` — Transport 底层：start_client/密钥交换/加密协商/认证/通道管理
5. `04-channel.md` — Channel：exec/shell/subsystem 通道、get_pty、resize、recv/send、exit_status
6. `05-authentication.md` — 认证体系：password/publickey/keyboard-interactive/gssapi、AuthStrategy、Agent
7. `06-keys-and-hostkeys.md` — PKey/RSAKey/Ed25519Key/ECDSAKey、HostKeys、MissingHostKeyPolicy 策略

**批次2（高级，4篇）**:
8. `07-sftp.md` — SFTPClient：put/get/file/stat/listdir/posix_rename/chmod/chown、SFTPFile、SFTPAttributes
9. `08-port-forwarding.md` — 本地/远程/SOCKS 转发、direct-tcpip channel、Tunnel
10. `09-server.md` — ServerInterface、SFTPServer、构建自定义 SSH 服务端
11. `10-advanced-patterns.md` — ProxyCommand 跳板机、连接池、并发通道、日志调试、异常处理最佳实践

### Step 4: 生成 examples/（5篇）
1. `basic-connection.md` — 基础连接与命令执行
2. `execute-commands.md` — 多种命令执行模式
3. `file-transfer.md` — SFTP 文件上传下载
4. `port-forwarding.md` — 端口转发隧道
5. `interactive-shell.md` — 交互式 shell 与 invoke_shell

### Step 5: 最后生成 index.md 文件
- `concepts/index.md`（无 frontmatter）
- `examples/index.md`（无 frontmatter）
- `references/index.md`（无 frontmatter）
- 根 `index.md`（带 okf_version: "0.2" frontmatter）
- `log.md`（记录 R/I/E/V 各阶段）

## Frontmatter 模板
```yaml
---
type: Concept  # 或 Example、Reference
title: <标题>
description: <30-80字摘要>
tags: [paramiko, <标签2>, <标签3>]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-source
    resource: /references/paramiko-source.md
---
```

## 文档格式规范
- 开头 1-2 段概述
- 使用 `##` 二级标题分节，不使用 `#`（留给文件标题）
- 代码块标注语言（python/bash）
- 每个文档结尾有 `## 相关概念` 章节
- 交叉链接使用 `/` 开头的 bundle-relative 路径（如 `/concepts/02-ssh-client.md`）
- 中文撰写，英文技术术语首次出现时括号注释
- 文件结尾可加信源脚注 `[^paramiko-source]`

## V 阶段（独立验证，必须执行）
1. **Grep API 验证**: 对文档中出现的每个类名和主要方法名，在 `external/libs/paramiko/paramiko/` 中 Grep 验证存在性
   - 必验类名: SSHClient, Transport, Channel, SFTPClient, SFTPServer, ServerInterface, MissingHostKeyPolicy, AutoAddPolicy, RejectPolicy, WarningPolicy, PKey, RSAKey, Ed25519Key, ECDSAKey, DSSKey, HostKeys, Agent, ProxyCommand, BufferedFile, SSHException, AuthenticationException, BadHostKeyException
   - 必验方法: connect, exec_command, invoke_shell, open_sftp, open_channel, start_client, start_server, set_missing_host_key_policy, get_transport, close, recv, send, recv_exit_status, request_pty, resize_pty, put, get, chdir, chmod, chown, stat, listdir, posix_rename, file, from_transport, request_port_forward, cancel_port_forward
2. **Frontmatter 检查**: 每个非 index/log 文件有 type/title/description/tags/generated/verified/status/stale_after/sources
3. **链接检查**: 所有 `/` 开头的链接目标文件存在
4. **虚构 API 修复**: 如发现 Grep 验证失败的 API，必须修正为真实 API

## 质量门
- G1: facts.md 无因果推断词
- G2: 洞察四元组完整
- G3: references 先生成、分批 ≤7、index 最后写
- G4: 零虚构 API（Grep 验证通过）、链接无断裂、frontmatter 完整

## 返回结果
完成后返回：
1. facts.md 中的事实总数
2. 生成的文件列表（完整路径）
3. V 阶段发现并修复的虚构 API 列表（如有）
4. 每个 Grep 验证的结果摘要
