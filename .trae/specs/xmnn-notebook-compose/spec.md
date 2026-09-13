# xmnn-whl-builder → .temp/notebook podman-compose 迁移 - Product Requirements Document

## Overview
- **Summary**: 将 `external/chaos/ai/xmnn-whl-builder`（Docker/BuildKit 谱系的 XMNN wheel 打包+运行时镜像）迁移表达为 `apps/containers/client/.temp/notebook/xmnn-whl-builder/` 下的 **podman-compose 声明式 notebook 工作负载栈**，配置模式以 OKF G1 知识包 `projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose` 为冲突裁决依据。
- **Purpose**: 用户在 podman machine（WSL2）内以 podman-compose 1.6.0 复刻官方示例（hello-python/tests）后，需要把真实重负载 xmnn-whl-builder 纳入同一 notebook 实验工作流：一条 `podman-compose up -d` 获得带 `xmnn-whl-builder` Jupyter 内核（cp314 GIL ABI）的 Notebook 服务，而非手工 `docker run`。
- **Target Users**: 在 `podman-machine-default` 内用 notebook 驱动 podman-compose 的开发者（本机单用户）。

## Goals
- 声明式运行栈：`compose.yaml` 单服务 `xmnn`，基于已构建的 `localhost/xmnn-whl-builder:latest` 启动 JupyterLab（8888），rootless 三必需与 client C11 compose 映射同源。
- 多文件 opt-in 覆盖（知识包 06 深合并模式）：
  - `compose.sources.yaml`：list 追加 npu_tvm/npuusertools 运行时 bind 挂载；
  - `compose.build.yaml`：为服务追加 `build:` 段（external/chaos 上下文 + 原 Dockerfile + PIP_MIRROR 参数），使 compose 也具备构建能力。
- 参数化：`.env.example` 承载镜像标签/容器名/端口/token/工作区/宿主源码路径，bash 风格 `${VAR:-default}` 插值。
- 冒烟资产：`workspace/smoke.ipynb` 验证 xmnn-whl-builder 内核可 import tvm/vta/xmnn 且 tvm.build(LLVM) 向量计算正确。
- 源目录零修改：`external/chaos/` 下任何文件不改动；client Python 包与 quant.* 命名空间零修改（.temp 临时区不回流产品代码）。

## Non-Goals
- 不在 compose 内实测全量 Nuitka 构建（10-30 分钟；构建路径仅静态验证 `config` 解析 + wrapper 可执行性，镜像已预构建存在）。
- 不新增 invoke 命名空间/不修改 `src/jpman_client/`、不新增 `quant.*` 同类正式叠加层（.temp/ 为 gitignored 临时实验区）。
- 不迁移 xmnn-runtime/xmnn-releases/xmnn-client/xmnn-package（镜像矩阵其余四层）。
- 不启用 SSH（22 端口不发布；原镜像 ENTRYPOINT 已清空、无 supervisord 拉起 sshd，notebook 单入口 8888）。
- 不做 GPU/CDI 设备编排（nvidia CDI 在本机不可用，test.ipynb 已实证失败；VTA 走 sim）。
- 不创建 git commit（.temp/ 被 .gitignore 排除；用户未要求提交）。

## Background & Context
- 源镜像两阶段构建（Dockerfile）：py314-base（conda base 升级 cp314 GIL）→ builder（Nuitka 编译 + bind mount 源码 + ccache）→ final（装 wheel、11 项验证、JupyterLab≥4.4、注册 xmnn-whl-builder 内核）。`ENTRYPOINT=[]`，默认 CMD 仅打印版本；镜像暴露 22/8888。
- 运行时实况（2026-09-13 实证）：`podman-machine-default`（Running）内存在 `localhost/xmnn-whl-builder:latest`（5.2GB，4 天前）、`localhost/devcontainer-base:onnx-quantized-latest`（3.5GB）；JupyterLab 4.6.3；内核 `xmnn-whl-builder` 位于 `/root/.local/share/jupyter/kernels/`，argv 指向 `/opt/conda/bin/python`（cp314 GIL），另含 main/python3 内核；`/workspace` 属 devuser:devuser。
- 目标区现状：`.temp/notebook/` 已有 compose 实验样本（compose.yaml 的 cuda GPU 测试、hello-python 复刻官方 examples/08、tests 最小 build）；test.ipynb 记录了 `!podman-compose up -d/down -v` 的交互方式与 GPU CDI 失败；残留 `notebook_test_1` Created 容器。
- 环境：machine 内 `/home/user/.local/bin/podman-compose` = 1.6.0，podman 5.7.1；宿主仓库经 9p 挂为 `/mnt/d/spaces/SpecWeave`。
- 已验证模式参照：client `overlays/onnx-quantized/`（2026-09-13 迁移）已确立「长语法 bind、三必需标准字段（devices/security_opt/cgroupns）、env 插值、labels 溯源、Windows 原生门禁」compose 范式。
- 构建兼容坑（源 docker-wrapper.sh/build.sh 实证）：podman/buildah 需 `--format docker`（OCI 忽略 SHELL/HEALTHCHECK）；buildah 不支持 .dockerignore 的 `**` globstar 与行内注释，需 sed 幂等 patch/restore。
- 方法论：seven-concepts 场景3（重构优化 I→F→A→C），V 由 Spec Mode 独立审查承担；知识包引用 concepts/02、03、06、08。

## Functional Requirements
- **FR-1**: `compose.yaml` 定义服务 `xmnn`：镜像 `${XMNN_IMAGE_TAG:-localhost/xmnn-whl-builder:latest}`，容器名插值，启动 main 环境 JupyterLab（`--ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=/workspace/notebooks --ServerApp.token=${JUPYTER_TOKEN 受控}`），发布 `${XMNN_JUPYTER_PORT:-8888}:8888`。
- **FR-2**: 服务携带 rootless 三必需（compose 标准字段 `devices: /dev/fuse`、`security_opt: label=disable`、`cgroupns: host`），全栈无 `privileged: true`；带 org.specweave labels。
- **FR-3**: 工作区以长语法 bind 挂入（默认源 `../../workspace` 相对 compose 文件，env 可覆盖为绝对路径；target `/workspace/notebooks`，`bind.create_host_path: true`）。
- **FR-4**: `compose.sources.yaml` 仅以 list 追加方式新增 npu_tvm→`/workspace/npu_tvm`、npuusertools→`/workspace/npuusertools` 两个长语法 bind（宿主路径由 .env 提供，默认指向 `/mnt/d/spaces/SpecWeave/external/chaos/...`），不替换 FR-3 挂载。
- **FR-5**: `compose.build.yaml` 为服务追加 `build:`（context 指向 external/chaos 仓库根的相对路径，dockerfile `ai/xmnn-whl-builder/Dockerfile`，args.PIP_MIRROR 透传 `${PIP_MIRROR:-aliyun}`）；与 image 共存（compose 语义：镜像缺失时构建）。
- **FR-6**: `.env.example` 以注释列出全部插值变量及默认值；不创建真实 `.env`。
- **FR-7**: `build-compose.sh`（bash，machine 内运行）幂等完成：`export BUILDAH_FORMAT=docker`、对 external/chaos/.dockerignore 做 globstar/行内注释临时 patch 并 trap restore、调用 `podman-compose -f compose.yaml -f compose.build.yaml build "$@"`；支持透传 PIP_MIRROR。
- **FR-8**: `workspace/smoke.ipynb` 为最小单代码单元 notebook：`import tvm, vta, xmnn` + `tvm.build`（LLVM target）向量加法断言，打印版本；在 xmnn-whl-builder 内核下可被 `jupyter nbconvert --to notebook --execute` 跑通。

## Non-Functional Requirements
- **NFR-1（知识包一致性）**: 所有 compose 写法可在 OKF podman-compose 知识包 concepts/02/03/06/08 找到依据：标准字段优先、不滥用 x-podman；多文件合并遵循 list 追加/按 target 去重；插值仅用文档支持的 6 种 bash 操作符子集（`:-`）。
- **NFR-2（rootless 安全）**: 默认隔离（无 host 网络、无 privileged、无 docker.sock）；宿主端口 ≥1024；容器以 root 运行（rootless 下映射宿主普通用户，满足 Jupyter/内核写 /workspace 与内核路径要求）。
- **NFR-3（可清理性）**: `podman-compose down` 后无项目容器/网络残留；bind 挂载不删宿主任何文件；不产生命名卷。
- **NFR-4（最小侵入）**: 全部产物落在 `.temp/notebook/xmnn-whl-builder/` 单一目录；external/ 与 client 产品代码 git 状态零变化；不新建 *.md 说明文档（用法由 compose.yaml 头注释承载）。
- **NFR-5（可复跑）**: 重复 up/down 幂等；token 留空时 JupyterLab 自动生成 token 并打印于 `podman-compose logs`。

## Constraints
- **Technical**:
  - podman-compose 1.6.0 / podman 5.7.1，仅在 `podman-machine-default`（WSL2 rootless）内运行；Windows 原生不运行（同 quant.* 门禁认知）。
  - 镜像/内核 ABI 不可变：内核 argv 必须保持 `/opt/conda/bin/python`（cp314 GIL），compose 不得切换 main env python 执行 kernel。
  - 构建路径前置：`BUILDAH_FORMAT=docker`（wrapper 强制）；.dockerignore globstar 必须临时 patch。
  - 9p 宿主路径：工作区/源码默认 `/mnt/d/spaces/SpecWeave/...`，仅在 machine 内可解析。
  - compose 项目名取目录名 `xmnn-whl-builder`（含连字符合法）。
- **Business**: .temp/ 为 gitignored 实验区（client/.gitignore L35），产物不入库、不进入正式交付；与 onnx-quantized 正式叠加层定位严格区分。
- **Dependencies**: 预构建镜像 localhost/xmnn-whl-builder:latest 已存在（缺失时 FR-5 + FR-7 提供构建路径，需 external/chaos/npu_tvm 与 npuusertools 源码树在位）。

## Assumptions
- 用户在 podman machine 内（cd /mnt/d/.../xmnn-whl-builder）执行 podman-compose，与既有 notebook 样本操作方式一致。
- machine 内 rootless 具备 /dev/fuse（quant 栈已实证同字段）。
- 8888 端口在宿主未被占用；若占用可经 XMNN_JUPYTER_PORT 调整。
- 不挂载源码时镜像内 wheel 自包含，import 与 tvm.build 均可工作（wheel 已含 _libs/ 与 RPATH $ORIGIN）。
- ~~JupyterLab 4.6.3 显式传空 token 等价自动生成~~（实现期证伪 2026-09-13）：实测 `--ServerApp.token=` 空串语义=**免认证**（/api/contents 直连 200）；machine 日志驱动为 journald 且无 systemd journal，自动 token 无法经 logs 查看。故默认免认证（localhost scratch 栈），注释指引 `jupyter server list`，需要认证经 JUPYTER_TOKEN 设置。

## Acceptance Criteria

### AC-1: compose 配置静态正确性
- **Type**: `rule`
- **Given**: 位于 machine 内 `/mnt/d/spaces/SpecWeave/apps/containers/client/.temp/notebook/xmnn-whl-builder/`
- **When**: 执行 `podman-compose config`、`-f compose.yaml -f compose.sources.yaml config`、`-f compose.yaml -f compose.build.yaml config`
- **Then**: 三者退出码均为 0；默认输出含 1 个服务 xmnn、8888 端口、三必需字段、1 个工作区 bind；sources 合并后 bind 数为 3 且 target 去重；build 合并后 build.context 解析为 external/chaos 绝对路径且 dockerfile 为 `ai/xmnn-whl-builder/Dockerfile`
- **Pass Condition**: 上述 5 项断言全部成立（以 config 输出 grep 实证）
- **Evidence**: 命令输出粘贴/摘要入 tasks.md Completion Evidence

### AC-2: Notebook 栈 E2E 可用
- **Type**: `rule`
- **Given**: 镜像 localhost/xmnn-whl-builder:latest 存在于 machine
- **When**: `podman-compose up -d` 后等待健康，curl `http://127.0.0.1:8888/lab`，`podman-compose exec` 执行 kernelspec 列举与 cp314 python 导入
- **Then**: HTTP 返回 200/302（JupyterLab 可达）；kernelspec 含 `xmnn-whl-builder`；`/opt/conda/bin/python -c "import tvm,vta,xmnn"` 退出码 0；容器内 `/workspace/notebooks/smoke.ipynb` 可见
- **Pass Condition**: 4 项全过
- **Evidence**: curl 状态码、exec 输出、文件 ls 结果

### AC-3: 冒烟 notebook 在 xmnn 内核下通过
- **Type**: `rule`
- **When**: 容器内以 main env jupyter 执行 `jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=xmnn-whl-builder /workspace/notebooks/smoke.ipynb`
- **Then**: 退出码 0，输出 notebook 无 error 输出单元，含 tvm.build 向量加法结果（期望 5）
- **Pass Condition**: nbconvert 退出码 0 且结果断言成立
- **Evidence**: 执行输出与产物 .nbconvert.ipynb 校验摘要

### AC-4: sources 覆盖挂载实证
- **Type**: `rule`
- **When**: 以 `-f compose.yaml -f compose.sources.yaml up -d` 启动后 `ls /workspace/npu_tvm /workspace/npuusertools`
- **Then**: 两目录可列且含源码树标志文件（npu_tvm/version.py、npuusertools/AGENTS.md）
- **Pass Condition**: ls 退出码 0 且标志文件存在
- **Evidence**: exec ls 输出

### AC-5: 构建覆盖 wrapper 可用性（静态）
- **Type**: `rule`
- **When**: 执行 `bash build-compose.sh --help`（或脚本内前置检查路径）与 `BUILDAH_FORMAT` 断言；不触发实际 build
- **Then**: 脚本语法 `bash -n` 通过；运行时 export BUILDAH_FORMAT=docker 可追踪（`bash -x` 片段）；.dockerignore patch/restore 函数存在且 trap 注册
- **Pass Condition**: 3 项静态检查通过
- **Evidence**: bash -n 输出与 bash -x 关键行

### AC-6: 零侵入与清理
- **Type**: `rule`
- **When**: `git status --porcelain` 在主仓库检查（.temp 产物应不可见），external/chaos 工作树检查；`podman-compose down` 后 `podman ps -a --filter label=io.podman.compose.project=xmnn-whl-builder` 与 network ls
- **Then**: 主仓库 git 不出现 .temp 新增追踪；external/chaos 源码树无修改；down 后项目容器/网络为零
- **Pass Condition**: 3 项断言成立
- **Evidence**: git status 摘要、podman ps/network 输出

### AC-7: 知识包模式保真度
- **Type**: `rubric`
- **Dimension**: compose 配置与 OKF podman-compose 知识包模式（02/03/06/08）的对齐度（标准字段、rootless 卷/端口、插值、深合并、x-podman 克制）
- **Scale**: 1-5
- **Anchors**: 1 = 出现知识包明确反对的写法（旧式顶层 x-podman 字典、特权、短语法自动建宿主目录、列表覆盖误用）；3 = 可运行但 2 处以上无依据/偏离模式；5 = 每条非平凡写法均可在知识包指认章节，头注释标注引用
- **Pass Threshold**: >= 4
- **Evidence**: reviewer 逐条对照 compose.yaml/compose.sources.yaml/compose.build.yaml 注释引用与知识包章节

### AC-8: 产物原子性与极简度
- **Type**: `rubric`
- **Dimension**: 目录内文件单一职责、无冗余、无 README 类主动文档、命名与既有样本（hello-python/tests/overlays）风格一致
- **Scale**: 1-5
- **Anchors**: 1 = 文件混杂多职责或含复制粘贴的大段无效内容；3 = 存在 1-2 个可删文件/段落；5 = 每文件单一职责、最少必要集（compose×3 + .env.example + build-compose.sh + workspace/smoke.ipynb）
- **Pass Threshold**: >= 4
- **Evidence**: 目录树 + reviewer 逐文件职责说明

## Open Questions
- 无（范围与源码挂载两处分叉已经用户 2026-09-13 确认：运行栈+可选构建覆盖；源码 opt-in override）。
