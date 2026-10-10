---
type: Reference
id: "xuan-compose-sticker-10-pattern-checklist"
title: "可复用模式、端到端演练与验收清单"
tags: ["xuan-compose", "模式", "反模式", "验收清单", "迁移", "知识沉淀"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: 本 Wiki 全教程；七概念方法论 G2/G3 质量门；xuan-compose 源码与上游对等测试"
summary: "把案例抽象为可迁移模式『声明式创意流水线：服务-任务分离编排』，给出适用边界、核心步骤、反模式、端到端命令演练与验收清单，并迁移到 ETL/文档批处理/ML 推理后处理等领域。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 可复用模式、端到端演练与验收清单

## 三条核心洞察（I 阶段）

1. **编排的价值在于分离"确定性环节"与"模型判断环节"，而不是会起容器。** 证据：色幕去底是纯 Pillow/numpy、零费用、退出码可判定的一次性任务；生图依赖外部模型。把两者塞进同一个长驻服务会让本地可复现的步骤也背上密钥、网络与不确定性。行动：建模先按"长驻/一次性 × 确定/模型"两轴切分。
2. **密钥与端点沿"插值 → .env → secret"三层下沉，compose 正文保持零密钥、可提交。** 证据：插值支持 `${V:?}` 缺失即报错；文件 secret 只读挂 `/run/secrets/<name>`，环境 secret 缺变量即抛错。行动：任何会入库的编排文件都不允许出现密钥字面量（[validate_compose.py](examples/validate_compose.py) 第 5 条把它变成自动检查）。
3. **"库优先、import 零副作用"让静态验证成为默认动作。** 证据：`ComposeEngine()` 不读 argv、不起子进程；`config`/`--dry-run`/库断言三连无需 Podman。行动：把编排校验左移到 CI/预提交，而不是等 `up` 失败再排查。

## 模式：声明式创意流水线（服务-任务分离编排）

- **适用于**：一条生产流程里同时存在①需要外部能力（模型/API/GPU）的步骤与②纯本地、确定性、可离线复现的后处理；产物通过文件交换；需要在他人机器上"同一条命令复现"；希望密钥不入库、环境可切换。
- **不适用于**：步骤间是高吞吐低延迟的在线请求链路（应用消息队列/服务网格而非文件交换）；纯单容器即可承载、没有后处理与密钥治理需求的小工具；需要严格分布式编排语义（重试/补偿/定时）的场景（那是工作流引擎的领域）。
- **成熟度**：编排机制（compose 语义、run/secret/卷/依赖）由 xuan-compose 对上游的 940 个对等测试背书；创意流水线切分为**单案例教学**，迁移到新领域后请按本清单复核。

### 核心做法（6 步）

1. **画两轴表**：列出每个环节的"长驻/一次性"与"确定/模型"，确定切分边界（本案例：generator=模型、keychroma=确定一次性、gallery=可选长驻）。
2. **文件即接口**：用 bind 目录（`./in`、`./out`）做步骤间交接，产物文件名固定；容器内路径与宿主路径在 compose 里显式映射。
3. **配置全外置**：端点/模型/密钥走 `${VAR:-默认}`、`.env` 与 secret；compose 正文零字面密钥，镜像与供应商解耦。
4. **双形态镜像**：能长驻的服务同时提供 CLI 入口，用 `up -d` 跑服务、`run --rm --entrypoint ...` 跑批处理，复用同一镜像与依赖。
5. **确定性步骤退出码即验收**：一次性任务自检并返回明确退出码，`run` 原样透传，用 `&&/||` 或 CI 串联步骤。
6. **校验左移三连**：库断言脚本 → `config --quiet` → `--dry-run up`，全部不依赖真实守护进程。

### 反模式（至少 3 个，均来自本类场景的真实教训）

- **❌ 把密钥写进 compose 或烤进镜像层**：一旦入库即泄露，且换账号要重新构建。✅ 文件 secret/环境 secret + `.gitignore`。
- **❌ 用长驻服务硬跑一次性批处理**：为了抠一张图起一个 daemon、产物靠 `docker cp` 捞、容器永不退出。✅ `run --rm` + bind 输出 + 退出码。
- **❌ 让模型直接交付最终格式（如透明 PNG）且无校验**：通道正确性无法复现、失败无信号。✅ 拆成"模型出色幕稿 + 确定性去底 + Alpha 自检"。
- **❌ 用 `depends_on` 表达跨一次性任务的数据顺序**：它只管运行中服务的状态条件。✅ 由调用方顺序执行（`&&`/Make/CI），或在一个容器内顺序调用。
- **❌ 改完 compose 手动 down 再 up、甚至重建一切**：误删命名卷里的状态。✅ 再 `up` 触发配置哈希对账，只重建变化的服务及其在跑下游。
- **❌ 把命名卷当宿主交换目录**：产物在卷里、宿主看不见、还奇怪 `down` 后为何还在/没了。✅ 要拿走的产物用 bind，仅容器自用的缓存用命名卷。

### 检验标准（做完怎么知道做对了）

- [ ] `python validate_compose.py` 与 `xuan-compose config --quiet` 均通过，且全程不需要 API Key；
- [ ] `--dry-run up` 打印的服务、挂载、secret、端口与预期一致；
- [ ] 编排文件 grep 不到任何真实密钥；`.env`、`secrets/*` 已被忽略；
- [ ] 一次性任务在干净环境（无缓存卷）可一次跑通，产物直接出现在宿主 `./out`；
- [ ] 任务失败时退出码非零且能被外层捕获；成功时产物通过格式自检（本案例为 RGBA、四角 alpha=0）；
- [ ] 改任一处服务配置后再 `up`，只重建受影响服务及其在跑下游；
- [ ] 同一份 compose.yaml 仅改环境变量即可切换端点/模型，正文零改动。

### 跨领域迁移示例

- **ETL/报表**：`fetcher`（调外部 API 拉数，模型/外部步骤）→ `transformer`（纯 pandas/SQL 确定性清洗，`run --rm`，读 `./in` 写 `./out`，行数校验非零退出）→ `dashboard`（可选长驻预览服务）；密钥走 secret。
- **文档批处理**：`renderer`（调远程排版/翻译 API）→ `pdfize`（本地 pandoc/字体容器，确定性，退出码校验 PDF 页数）；`./manuscript` 进、`./dist` 出。
- **ML 推理后处理**：`infer`（GPU 长驻服务，[resources 支持 nvidia 设备参数](../../../../projects/xuanspace/libs/xuan-compose/src/xuan_compose/translate/resources.py)）→ `postprocess`（CPU 一次性容器做 NMS/导出/水印校验）；GPU 配额、模型缓存分别走 resources 与命名卷。

## 端到端演练（对照 [examples/README.md](examples/README.md)）

```bash
cd examples
cp .env.example .env
mkdir -p secrets photos out && printf '你的ARK_API_KEY' > secrets/ark_key.txt
cp ~/Photos/trip.jpg photos/in.jpg

# 零成本校验三连
python validate_compose.py
xuan-compose config --quiet
xuan-compose --dry-run up

# ① 模型步骤：照片 → 记忆卡 + 色幕贴纸稿
xuan-compose run --rm --entrypoint python generator \
  generate.py pipeline photos/in.jpg "Crater Smoke" "Blue Summit" "Quiet Ridge"
# ② 确定性步骤：色幕稿 → 透明 PNG（退出码 2 即未通过）
xuan-compose run --rm keychroma -- \
  /work/out/stickers-chroma.png /work/out/stickers.png \
  --soft-matte --despill --edge-contract 1
# ③ 可选长驻：API + 画廊
xuan-compose --profile web up -d        # http://localhost:8000 / :8080
xuan-compose --profile web down         # 清理也要带 profile，否则 gallery 不在解析范围会残留
```

完成后 `./out/` 下应有三份产物：`card.png`（完整记忆卡）、`stickers-chroma.png`（色幕稿，中间产物）、`stickers.png`（RGBA 透明底六贴纸，最终交付）。
