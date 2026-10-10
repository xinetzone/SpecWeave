# xuan-compose 实战：手帐贴纸风格照片生成 Wiki

以「一张照片 → 3:2 手帐旅行记忆卡 + 同图案透明底贴纸 PNG」双产物为实战案例，系统讲解 [xuan-compose](../../../../projects/xuanspace/libs/xuan-compose/README.md)（由 containers/podman-compose v1.6.0 翻译式分层重构的 Compose 规范声明式容器编排引擎）。配套可运行工程见 [examples/](examples/README.md)。

```{toctree}
:maxdepth: 2
:caption: 教程正文
:hidden:

00-overview
01-pipeline-architecture
02-install-discovery
03-compose-walkthrough
04-volumes-secrets
05-lifecycle-tasks
06-generator-worker
07-chroma-key-task
08-library-api
09-pitfalls-faq
10-pattern-checklist
```

```{toctree}
:maxdepth: 1
:caption: 配套工程
:hidden:

examples/README
examples/secrets/README
```

| 章节 | 主题 |
|------|------|
| [00 总览](00-overview.md) | 双产物案例、三个知识来源、能力地图、工作假设 |
| [01 流水线与架构](01-pipeline-architecture.md) | 两轴切分法、服务拓扑、xuan-compose 七层架构 |
| [02 安装与文件发现](02-install-discovery.md) | 安装、14 默认名、向上 10 层发现、项目名优先级、.env |
| [03 compose 逐段精讲](03-compose-walkthrough.md) | build/image、插值语法、profiles、合并、config 校验 |
| [04 卷与密钥](04-volumes-secrets.md) | bind/命名卷/tmpfs、文件与环境 secret、网络 |
| [05 生命周期与一次性任务](05-lifecycle-tasks.md) | depends_on 条件、healthcheck、up 对账、down、run --rm |
| [06 生图服务实战](06-generator-worker.md) | Seedream 5.0 Pro 接口事实、双形态镜像、提示词模板 |
| [07 色幕去底任务](07-chroma-key-task.md) | chroma-key 算法、退出码、RGBA 验收 |
| [08 库 API 与预演](08-library-api.md) | ComposeEngine、纯解析、无 Podman 校验三连 |
| [09 避坑与 FAQ](09-pitfalls-faq.md) | 上游怪癖、版本门槛、WSL、GPL、报错速查 |
| [10 模式与验收清单](10-pattern-checklist.md) | 可迁移模式、反模式、验收清单、跨领域迁移 |
