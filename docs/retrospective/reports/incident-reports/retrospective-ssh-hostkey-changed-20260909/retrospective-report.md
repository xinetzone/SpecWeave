---
id: "retrospective-ssh-hostkey-changed-20260909"
title: "inv run 后 SSH host key changed 复盘"
date: "2026-09-09"
source: "apps/containers/client 消费端 ensure_known_hosts 失效诊断 (2026-09-09)"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/incident-reports/retrospective-ssh-hostkey-changed-20260909/retrospective-report.toml"
type: incident-report
scope: task
status: completed
related_patterns:
  - "python-pathlib-tilde-no-expansion"
---

# inv run 后 SSH host key changed 复盘

## 事件概述

**发生时间**：2026-09-09
**影响范围**：`apps/containers/client` 消费端 `inv run` → 手动 `ssh -p 2222 devuser@localhost`
**严重程度**：P2（连接受阻，手工清除 known_hosts 可绕过）
**根因类别**：编码缺陷（Windows 无 `HOME` 环境变量 + pathlib `Path("~")` 不展开波浪号 → 清理逻辑静默失效）+ 设计时序缺陷（keyscan 预写在旧容器删除前执行会抓到过期 key）

## 事实时间线

| # | 事件 |
|---|------|
| F1 | entrypoint.sh `generate_host_keys()` 每次容器启动 `rm -f /etc/ssh/ssh_host_*_key` 后 `ssh-keygen -A` 重新生成 host key（镜像不携带预生成密钥的安全设计） |
| F2 | `apps/containers/client` `inv load` 成功加载 `localhost/jupyter-podman-rootless:latest` |
| F3 | 用户执行 `inv run` 重建容器（`_run_via_sdk`/`_run_via_cli` 先 `remove(force=True)` 旧容器再创建新容器） |
| F4 | 用户手动执行 `ssh -p 2222 devuser@localhost` 报 `REMOTE HOST IDENTIFICATION HAS CHANGED`，`Offending RSA key in C:\Users\xinzo/.ssh/known_hosts:20` |
| F5 | 检查 `C:\Users\xinzo\.ssh\known_hosts`：第 19 行 ed25519、第 20 行 rsa 均为 `[localhost]:2222` 旧 key |
| F6 | 检查 `clean`（原 `ensure_known_hosts`）代码：`known_hosts_path = Path(os.environ.get("HOME", "~")) / ".ssh" / "known_hosts"` |
| F7 | 实测（Windows PowerShell 环境）：`os.environ.get("HOME")` 返回 `None`；`Path("~")` 得到 `WindowsPath('~')`（字面量目录）；`.exists()` 返回 `False`；`Path.home()` 返回 `C:\Users\xinzo` |
| F8 | 定位到函数在 `if not known_hosts_path.exists(): return` 处静默返回，known_hosts 清理从未执行 |
| F9 | 识别次生时序缺陷：即使路径正确，原函数在容器启动前用 ssh-keyscan 预写 key；同名旧容器若仍在运行，keyscan 抓到的是旧容器 key，新容器启动后冲突依旧 |
| F10 | 修复后真实调用 `clean_stale_host_keys()`：成功清理 known_hosts 中 2 条过期条目，`cleaned: True` |

## 根因分析（5Why）

```
为什么 ssh 报 REMOTE HOST IDENTIFICATION HAS CHANGED？
├─ 为什么？→ known_hosts 中 [localhost]:2222 记录与新容器 host key 不一致
│   └─ 为什么？→ 容器重建后 entrypoint 重新生成 host key（安全设计），known_hosts 未同步
│       └─ 为什么？→ ensure_known_hosts 本应在 inv run 时清理旧条目，但未生效
│           └─ 为什么？→ Path(os.environ.get("HOME","~")) 在 Windows 得到 WindowsPath('~')
│               字面量，exists() 恒 False，函数静默 return（实验 F7 证实）
│               └─ 为什么？→ pathlib 不展开波浪号；HOME 在 Windows PowerShell 中不存在
├─ 次生缺陷？→ 原实现 keyscan 预写在旧容器删除前，若旧容器存活会抓取过期 key
```

## 洞察

| # | 陈述 | 证据 | 反常识 | 行动 |
|---|------|------|--------|------|
| I1 | 用户家目录路径必须用 `Path.home()` 而非 `Path(os.environ.get("HOME","~"))` | F7 | `Path("~")` 是**字面目录**不是主目录，波浪号展开是 shell 行为而非 pathlib 行为 | 全仓审计 `.ssh`/`.config`/`.aws` 等用户路径构造，统一 `Path.home()` |
| I2 | "启动前清理 + keyscan 预写新 key" 是时序反模式：预写发生在目标资源（新容器）诞生前 | F9 | 预取远程状态若早于资源生命周期变更，抓到的反而是即将消亡的旧状态 | 预清理与状态获取分离：clean 在启动前，refresh 在启动后 |
| I3 | 静默失效比显式报错更危险：exists() 为 False 时直接 return 掩盖了路径构造错误 | F7/F8 | "文件不存在所以无需清理"与"路径算错所以没找到文件"无法区分 | 关键防御逻辑失败时应打 WARN 日志而非静默返回 |

## 修复措施与验证

- **A1（已提交 a5ab75d75）**：
  - [utils.py](../../../../../apps/containers/client/src/jpman_client/tasks/utils.py)：
    - `clean_stale_host_keys()`：改用 `Path.home()`；仅清理（移除 keyscan 预写）；正则限定 `localhost`/`127.0.0.1`
    - `refresh_host_keys()`：detach 启动后短轮询 sshd，keyscan 追加新 key（只追加不重建文件）
  - [manage.py](../../../../../apps/containers/client/src/jpman_client/tasks/manage.py)：`run()` 顺序改为 `clean → run_container → (detach) refresh`
- **验证**：`py_compile` 通过；真实调用 `clean_stale_host_keys()` 清理 2 条过期条目成功；语法与 import 无残留 `ensure_known_hosts` 引用

## 预防行动项

| # | 行动 | 状态 |
|---|------|------|
| A1 | 代码修复（clean/refresh 拆分 + `Path.home()`） | ✅ `a5ab75d75` |
| A2 | 沉淀模式 `python-pathlib-tilde-no-expansion`（code-patterns） | ✅ |
| A3 | 本复盘报告落盘 | ✅ |

## 质量门记录

- **V 门**：对修复方案执行 4 视角对抗审查，采纳 3 条修正（keyscan 后置、限定 localhost、只追加不重建）
- **G4**：A1 单一职责（仅 host key 管理）；预提交 Hook 全部通过（敏感信息/模式 V2/并发安全）
