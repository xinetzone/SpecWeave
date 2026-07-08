---
name: "<module-name>-onboarding"
version: "1.0.0"
last_updated: "YYYY-MM-DD"
schema: "l0-onboarding-v1"
max_lines: 100
title: "<模块名称> Onboarding"
x-toml-ref: "../../.meta/toml/.agents/capabilities/ONBOARDING-TEMPLATE.toml"
---
# <模块名称> Onboarding

> **这是什么？** <一句话身份声明：本模块/子系统是什么，提供什么能力>
>
> **阅读时间**：< 30秒。Agent 新会话接入本模块时的第一份必读文档。
> 遵循[渐进式披露三层架构](ARCHITECTURE.md)规范。

---

## 快速开始（3步）

```
步骤1：你正在读本文件 ✅
步骤2：读取 REGISTRY.md 了解有哪些能力可用
步骤3：按下表路由到对应能力，按需加载详细文档
```

---

## 能力速查表

| 你要做什么 | 应该用什么 | 去哪里找 |
|-----------|-----------|---------|
| **<操作1>**（<触发词>） | <能力名> | `path/to/SKILL.md` |
| **<操作2>**（<触发词>） | <能力名> | `path/to/SKILL.md` |
| **<操作3>**（<触发词>） | <能力名> | `path/to/SKILL.md` |
| **<操作N>** | <能力名> | REGISTRY.md |

---

## 必知 vs 按需

| 文档 | 何时读 | 优先级 |
|------|--------|--------|
| 本文件 + REGISTRY.md | **每次进入本模块必读** | 🔴 必须 |
| <关键规范文档> | <触发场景> | 🟡 按需 |
| <其他模块文档> | <触发场景> | 🟢 按需 |

> 💡 **原则**：不要预读所有文档。先用速查表定位目标能力，再读取该能力的SKILL.md。

---

## 任务路由

```
收到本模块相关任务？
├─ <任务类型1>？ → <对应SKILL.md>
├─ <任务类型2>？ → <对应SKILL.md>
├─ <任务类型3>？ → <对应SKILL.md>
└─ 不确定？ → 查 REGISTRY.md
```

---

## 启动确认格式

进入本模块时，请确认：

```
📋 <模块名>上下文已建立：已读 ONBOARDING.md + REGISTRY.md
任务类型识别：<类型>
将使用：<对应能力>
```

---

## 模板使用说明

> 创建新模块的ONBOARDING.md时：
> 1. 复制本模板到目标目录，重命名为 `ONBOARDING.md`，替换所有 `<placeholder>`
> 2. 路径列填写实际的Markdown链接（如 `[skil名](path/to/SKILL.md)`）
> 3. 总行数严格控制在100行以内（不含本说明块）
> 4. 删除本"模板使用说明"区块
> 5. 对照 [ARCHITECTURE.md](ARCHITECTURE.md) 第五节L0检查清单验证
