---
type: Reference
id: "xuan-compose-sticker-08-library-api"
title: "库 API 与无 Podman 预演：把编排错误挡在起容器之前"
tags: ["xuan-compose", "库-api", "dry-run", "静态校验", "python314"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: xuan-compose README.md 库 API 章节、src/xuan_compose/engine.py、cli/parser.py、cli/main.py、translate/mounts.py；examples/validate_compose.py"
summary: "xuan-compose 不只是 CLI：import 零副作用，ComposeEngine 是纯状态对象，parse_args 纯解析回写，_parse_compose_file 可在 Python 中完成发现/插值/合并/规范化；配合 config、--dry-run 与一段断言脚本，可在没有 Podman 的环境里把绝大多数编排错误挡下来。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 库 API 与无 Podman 预演

## 三层"不动真格"的验证手段

| 手段 | 覆盖管道 | 需要 Podman？ |
|------|---------|:---:|
| `xuan-compose config [-q]` | 发现→.env→插值→合并→规范化 | 否 |
| `xuan-compose --dry-run up` | 再加翻译层、模拟执行（打印将执行的 podman 调用） | 否 |
| 库 API + 自定义断言 | 在 Python 里对规范化结果做**任意**程序化检查 | 否 |

xuan-compose 的上游单体在 import 期就有全局状态与 argv 读取；重构后**库优先**：`import xuan_compose` 不读 argv、不建引擎、不起子进程，`sys.argv` 的真实读取只存在于 `cli/main.py` 单点。这让编排文件可以像配置数据一样被程序加载和检验（xuan-compose 自己的 940 个单测也全部 fake 子进程、无需真实 Podman）。

## 库 API 的三种用法

### ① 纯解析参数（无文件也能跑）

```python
from xuan_compose.cli.parser import parse_args
from xuan_compose.engine import ComposeEngine

engine = ComposeEngine()                  # 纯状态对象
args = parse_args(engine, ["-f", "compose.yaml", "config", "--quiet"])
print(args.command, args.file)            # config ['compose.yaml']
# engine.global_args 已同步回写
```

### ② 加载并检视规范化结果（cwd 需能发现 compose 文件）

```python
engine._parse_compose_file()
print(engine.project_name)                # sticker-studio
print(sorted(engine.all_services))        # ['gallery', 'generator', 'keychroma']
print(engine.services["generator"])       # 规范化后的服务字典
print(engine.merged_yaml)                 # 合并+插值+规范化后的 YAML 文本
# 其他可读状态：engine.containers / engine.yaml_hash / engine.declared_secrets / engine.vols
```

### ③ 完整运行时（装配 Podman、探测版本、分发命令）

```python
import asyncio
from xuan_compose.cli.main import async_main

asyncio.run(async_main(["--dry-run", "-f", "compose.yaml", "up"]))
```

翻译层的纯函数也能脱离引擎单独使用，例如验证短挂载语法：

```python
from xuan_compose.translate.mounts import parse_short_mount
parse_short_mount("./out:/work/out", basedir=".")
# {'type': 'bind', 'source': '.../out', 'target': '/work/out', ...}
```

## 落地：给 sticker-studio 写一个编排断言脚本

[examples/validate_compose.py](examples/validate_compose.py) 用库 API 把"人肉 review compose.yaml"变成可重复检查：

```bash
cd examples
python validate_compose.py
# 编排校验通过：项目='sticker-studio'，服务=['gallery', 'generator', 'keychroma']
```

它断言的正是前几章那些**容易漏、且要到 `up` 之后才暴露**的约束：

1. 三个服务齐备；
2. `generator` 有 `healthcheck`（否则 `gallery` 的 `service_healthy` 依赖无意义）、引用了 `ark_key` secret、挂了三个工作目录；
3. `gallery` 在 `web` profile 下且健康依赖 `generator`；
4. 命名卷 `gen-cache` 已在顶层声明（未声明在运行期才抛 `RuntimeError`）；
5. 合并结果里**没有** `ARK_API_KEY=` 字面量（防密钥硬编码入库）；
6. 顺带用纯函数验证 `./out:/work/out` 被识别为 bind。

## 建议的验证三连

```bash
python validate_compose.py                 # ① 自定义结构断言（最快、最贴业务）
xuan-compose config --quiet                # ② 引擎自己的解析校验
xuan-compose --dry-run up                  # ③ 看翻译出的 podman 调用序列
```

把第 ①② 步放进 CI 或 pre-commit，就能在**没有 Podman、没有 API Key、不产生任何费用**的前提下，拦住绝大多数编排缺陷；真正的容器行为只留给带 Podman 的环境验证。这也解释了为什么 xuan-compose 要被重构成"库 + CLI"双入口而不是只有一个脚本——**可被程序加载的编排，才是可测试、可审计的编排**。
