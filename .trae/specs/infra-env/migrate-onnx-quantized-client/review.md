# onnx-quantized 迁移至 apps/containers/client - Independent Review

- [x] CP-R1: 量化叠加镜像、守卫与三冒烟满足 AC-1/AC-2
  - **Type**: `rule`
  - **Covers**: AC-1, AC-2 / TR-1.x, TR-2.x, TR-5.1
  - **Evidence**: R1 独立运行 `podman run --rm ... _quant_guards.py` 实测打印五包版本（onnx 1.22.0/onnxruntime 1.28.0/onnxscript 0.7.1/onnxconverter-common 1.16.0/onnxsim v0.7.3）+ `[OK] guards: cp314t + GIL off + torch/torchvision/onnxoptimizer absent`；inspect 证实 Entrypoint/CMD/WORKDIR 沿用基底；Containerfile grep 无 ENTRYPOINT/CMD/SHELL 覆盖。**pass**

- [x] CP-R2: compose 栈合法、rootless 安全且可 up/down（AC-3）
  - **Type**: `rule`
  - **Covers**: AC-3 / TR-3.x, TR-5.2
  - **Evidence**: 审查员独立以真 podman-compose 1.6.0 双文件 config 渲染：默认含 /dev/fuse、label=disable、cgroupns:host、长语法 bind；GPU 叠加后 devices=[/dev/fuse,/dev/dri] 无重复；无 privileged/短语法/x-podman。up/端口/down 部分采用实施方 T5 实测证据（SSH banner/HTTP 302/零残留）+ 审查员镜像可运行性间接覆盖（委托约定审查员不起停栈）。**pass**

- [x] CP-R3: quant.* 命名空间、双门禁、可选依赖与零回归（AC-4/5/6）
  - **Type**: `rule`
  - **Covers**: AC-4, AC-5, AC-6 / TR-4.x, TR-5.3
  - **Evidence**: 审查员实测 invoke --list = 23 任务（7+7+3+6）；grep 无 podman 导入；核心 dependencies 零 diff + [compose] extra；Windows 门禁 Exit(1) 双路径、monkeypatch 缺二进制 Exit(1) pip 指引均独立复现；12 插值键双 .env 一一对应。**pass**

- [x] CP-R4: 文档/治理同步、互链可达、源目录零改动（AC-7）
  - **Type**: `rule`
  - **Covers**: AC-7 / TR-6.x, TR-7.1, TR-7.2
  - **Evidence**: 审查员核对 git status（源变体目录空；新增仅在 client/ 与 .trae/specs/）、check-links 95 个本地引用全存在（4 目录警告为既有条目）、三冒烟逐行等价比对无放宽、迁移指南仅在「Docker 谱系（源）」对比列残留 --privileged/2375 字样（属明确标注）。**pass**

- [x] CP-U1: 与 podman-compose 知识包的架构对齐度（AC-U1）
  - **Type**: `rubric`
  - **Covers**: AC-U1
  - **Scale**: 1-5
  - **Anchors**: 1 = 照搬 Docker compose 习惯/短语法/特权；3 = 能跑通但 x-podman 滥用或双 .env 混乱；5 = 标准字段优先、override 分层正确、标签接缝成立、门禁与构建端一致
  - **Pass Threshold**: >= 4
  - **Evidence**: 审查员评 **5/5**——标准字段表达三必需（概念 03）、零必要 x-podman（08）、list 追加合并经 1.6.0 双渲染实证（06）、标签键 io.podman.compose.project/service 与 podman-compose 源码逐字一致（05 接缝）、双源优先级三处文档说清、门禁对齐构建端教训。

- [x] CP-U2: 量化能力迁移保真度（AC-U2）
  - **Type**: `rubric`
  - **Covers**: AC-U2
  - **Scale**: 1-5
  - **Anchors**: 1 = 丢包/丢守卫/阈值放宽；3 = 包齐但版本漂移无据或文档残留 Docker 主路径；5 = 版本三重实证、守卫与冒烟全保留、OMP 一致、DinD→rootless 改写清楚
  - **Pass Threshold**: >= 4
  - **Evidence**: 审查员评 **5/5**——版本经源浮动 Dockerfile + RELEASE 矩阵 + PyPI 索引三重实证（0.5.0↔0.7.3 异构三处留证）；守卫严于源（补 torchvision）；OMP 四件套一致；三冒烟逐行等价且独立跑出相同数值；neural-compressor 边界清楚。

- [x] CP-U3: client 工程整洁度（AC-U3）
  - **Type**: `rubric`
  - **Covers**: AC-U3
  - **Scale**: 1-5
  - **Anchors**: 1 = 逻辑堆砌/重复实现；3 = 功能完整但边界模糊；5 = 单一职责、DRY、复用 utils、中文诊断可执行
  - **Pass Threshold**: >= 4
  - **Evidence**: 审查员评 **5/5**——quant.py 296 行单一编排职责，复用 6 个既有助手零重复；overlay 自包含小上下文；双门禁文案可执行；私有函数跨模块引用仅限同包内部复用。

## Review History

### Review R1
- **Result**: `pass`
- **Reviewer**: 独立 general_purpose_task 代理（全新上下文、只读，禁止修改文件与起停栈）
- **Evidence**:
  - 4 规则检查点全部 pass（无 blocked）；3 rubric 均 5/5（阈值 ≥4）
  - 独立复现：镜像守卫/1 冒烟容器执行、podman-compose 1.6.0 双 config 渲染、invoke --list 23 任务、双门禁 Exit(1)、git 源目录零改动、check-links 95 引用全通过、三脚本逐行等价
  - **Findings**: 0 actionable；3 条 low advisory（F-1 根 .env quant 段全注释可加说明；F-2 up 不透传 PIP_MIRROR 可在 help 提示；F-3 注入面深水区审查无问题）
  - **Advisory 闭环（实施方，2026-09-13）**：F-1 已在根 .env.example 段首补「默认全部注释，按需取消注释」；F-2 已在 quant.py `up` 任务上方补两步路径注释；F-3 无需改动。修订后 quant.py py_compile 复检通过。
- **Blocked By**: 无
