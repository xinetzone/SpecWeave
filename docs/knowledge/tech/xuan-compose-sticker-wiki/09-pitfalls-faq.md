---
type: Reference
id: "xuan-compose-sticker-09-pitfalls-faq"
title: "避坑、上游怪癖与 FAQ"
tags: ["xuan-compose", "避坑", "faq", "怪癖", "wsl", "许可证"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: xuan-compose docs/parity.md §5.3、README.md、CHANGELOG.md、src/xuan_compose 各模块"
summary: "汇总 xuan-compose 刻意保留的 podman-compose 上游怪癖（退出码 -1、时间解析、./ 前缀、tag 百分号编码、ls 非标准 JSON 等）、版本门槛、Windows/WSL 取舍、GPL-2.0 许可边界，以及本案例高频报错的定位与处理。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 避坑、上游怪癖与 FAQ

## 刻意保留的"上游怪癖"（不是 bug，对等重构不擅自修）

xuan-compose 对 podman-compose v1.6.0 逐行对等，以下行为被测试固化、**不会**被"顺手修正"，写脚本时要知道：

1. **无参数 / `help` 的退出码是 `-1`**（不是常见的 0 或 1）。不要在 shell 里用 `xuan-compose help` 的退出码判成败。
2. **时间字符串解析**：`stop_grace_period`/`-t` 接受 `"1:30"` 或 `"1m30s"`，但 `"1m:30s"` 会解析失败返回 `None`；只接受整数秒语义。
3. **`./` 前缀不剥离**：`volumes` 短格式、`env_file`、`sub_dir` 里的 `./` 会原样保留（只有 `build.context` 分支剥离）。本教程统一写 `./photos:/work/photos` 是可工作的，但别指望它被规范化成绝对路径再显示。
4. **镜像 tag 冒号会被百分号编码**：构建附加上下文相关逻辑里 `b:1` 可能被 quote 成 `b%3A1`（`urllib.parse.quote`），涉及镜像名拼接时留意。
5. **`ls --format json` 输出不是标准 JSON**：它是 Python 的 `print(list)`（单引号、`True/False/None`），不要直接喂给 `json.loads`；要机器解析请用 `podman` 原生命令或 `ps --format`。
6. **`--pull-always false` 静默无效**：该 argparse 动作对显式 false 直接 return 不赋值；要表达"不强制拉取"就别传这个参数。
7. **`run --service-ports` 为假时会先删掉服务 ports 再由 `--publish` 重建**，原端口映射不保留；想保留服务端口请用 `--service-ports`，临时加端口用 `-p`。
8. **依赖图容错**：自依赖/未知依赖会"保留边但不展开"，A→B→A 的环按起点剪枝而不是报错——所以依赖名拼错可能不报错而是被忽略，`config` 后务必人工核对。
9. **`is_list(bytes)` 为 True**：纯 Python 3.14 下 bytes 被视作列表类输入，这是上游语义。

完整清单见库内 [docs/parity.md](../../../../projects/xuanspace/libs/xuan-compose/docs/parity.md) §5.3。

## 版本门槛

| 能力 | 门槛 | 不满足时 |
|------|------|---------|
| `up --wait` 等 `running\|healthy`、依赖等 `healthy/unhealthy` | podman ≥ **4.6.0** | 告警并跳过等待 |
| `up` 前的显式预拉优化（缩短停机） | podman ≥ **5.6.0** | 退化为 `podman create` 隐式拉取（仍可用） |
| 安装 xuan-compose | Python ≥ **3.14** | 安装失败 |

## Windows / WSL 取舍

- 权威运行/测试环境是 **WSL + Python 3.14**（POSIX 路径语义，与上游 CI 一致，940 例全绿）；Windows 原生主要是 ruff/mypy 门禁。
- 原生 Windows 上 `\`/`/`、盘符根、`os.path.join` 尾段存在已知差异，与上游在 Windows 上的行为**同构**（非重构引入）。涉及 `.sock` 挂载时代码对 Windows 有专门分支。
- 结论：**在 WSL2 里装 Podman 并跑本教程**，少踩一类路径坑。

## 许可边界

xuan-compose 继承上游 **GPL-2.0-only**（96 个 `.py` 带 SPDX 头），**不得重新许可**。你基于它分发衍生作品或镜像时需遵守 GPL-2.0 义务；内部自用与通过容器提供服务的边界请自行评估。本教程配套示例代码沿用同样的 SPDX 头。

## 本案例高频报错速查

| 报错/现象 | 原因 | 处理 |
|-----------|------|------|
| `Named volume ... no declaration was found in the volumes section` | 用了命名卷却没在顶层 `volumes:` 声明 | 补声明，或改用 `./` 开头的 bind |
| `ValueError: undeclared secret` | 服务引用了顶层没声明的 secret | 在顶层 `secrets:` 声明，或修正引用名 |
| `Environment variable ... required by secret ... is not set` | 环境 secret 取值变量缺失 | `export`/`.env` 提供该变量后再 `up` |
| `networks` 与 `network_mode` 同存报错 | 二者互斥 | 每个服务二选一 |
| external 网络/卷缺失的友好错误 | `external: true` 资源未预先创建 | 先 `podman network create` / `volume create` |
| `gallery` 没等 generator 健康就启动 | podman 版本 < 4.6.0 或没配 healthcheck | 升级 podman；给 generator 补 healthcheck |
| 第二个服务起不来，日志报端口已被占用 | 默认 `in_pod=true`，同 Pod 共享 netns，两个容器监听同一容器端口 | 让同 Pod 各服务监听不同容器端口（如 generator 8000、gallery 8080） |
| 去底退出码 2（四角不透明） | 幕布不均/阈值过小/图案色撞幕色 | 见 [07 章](07-chroma-key-task.md)调参表；绿植场景换 `#ff00ff` 重生成 |
| `image` 参考图请求报错 | 端点不接受 data URI，只接受 URL | 把图放到可访问 URL，改传 `image_url` |
| 改了 compose 不生效 | 用了 `--no-recreate`，或改的是镜像内容但 tag 没变 | 再 `up`（配置哈希对账）；镜像内容变化走 `--build` 或唯一 tag |

## 几个"该在哪做"的设计问答

- **为什么不直接让模型出透明 PNG？** 见 [06 章](06-generator-worker.md)：双步把视觉一致性与通道正确性分开，各自可校验；模型直出透明可作备选但不保证与卡面同版。
- **为什么密钥不直接写 `environment`？** 能写（`${ARK_API_KEY:?}`），但文件 secret 默认不进进程环境、不落镜像层、挂载只读，泄露面更小，见 [04 章](04-volumes-secrets.md)。
- **为什么去底不放进 generator 镜像一步做完？** 确定性环节与模型判断环节的依赖、失败模式、费用模型完全不同；拆开后去底可离线重跑、可独立测退出码，生图服务也不必带图像处理依赖。
