# agent-monetize-dev 叠加层 - Implementation Plan

> 由 **client-overlay-scaffold** 技能驱动；三骨架（compose/.env/namespace）
> 从技能 templates/ 渲染（dogfood），Containerfile/builder/scripts/smoke
> 按形态 B 轻量变体特化。所有容器命令在 WSL2 podman-machine-default 执行。
> 移植/范式真源：技能 SKILL.md + xmnn-dev overlay + xmnn.py；
> 目标源码 apps/agent-monetize（只读挂载，仅 3 处跨平台适配）。

## Task 1: 脚手架骨架渲染与 overlay 目录
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `apps/containers/client/overlays/agent-monetize-dev/{builder/scripts/lib,smoke,scripts}`。
  - 从 `.agents/skills/client-overlay-scaffold/templates/` 复制三骨架并替换：
    `__STACK__=agent-monetize-dev`、`__NS__=monetize`、`__SVC__=monetize`、
    `__ENV_PREFIX__=MONETIZE`、`__IMAGE__=localhost/agent-monetize-dev:latest`、
    `__SSH_PORT__=2224`、`__JUPYTER_PORT__=8892`、
    `__CONTAINERFILE__=Containerfile.agent-monetize`。
  - 按 FR-3 增删：volumes 只留 workspace + agent-monetize 两个 bind
    （去掉形态 B 通用的多余注释卷，保留 ccache 可选注释）；环境变量加
    PYTHONPATH/LD_LIBRARY_PATH；build args 去 CONDA_MIRROR（apt/pip 栈
    不需要 conda 源）。
  - 先核对 Q1 相对路径层级（podman-compose config 绝对化后 target 可见
    真实 agent-monetize）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 占位符 `__X__` 在成品中 0 残留（仅注释中的说明除外）。
  - `rule` TR-1.2: `podman-compose config` 退出 0 且 bind 恰 2、
    target /workspace 与 /workspace/agent-monetize 均解析到真实目录。
  - `rule` TR-1.3: .env 键集合与 compose 插值键 diff 空。

## Task 2: vendor logging.sh + 构建脚本（build-native / build-wheel）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 复制 xmnn-dev 的 `builder/scripts/lib/logging.sh`（vendor，去 chaos
    路径化）。
  - `build-native.sh`：set -Eeuo pipefail；SRC_ROOT/CC/CXX 环境变量化；
    从 `/opt/conda/bin/python` 取 site-packages→tvm_ffi include/lib；
    clang++ 编译参数（-std=c++17 -shared -fPIC -O2 -I -L -ltvm_ffi -o
    native/build/score_opportunity.so）；patchelf --set-rpath 到
    tvm_ffi/lib（Q2，LD_LIBRARY_PATH 双保险）；缺 .cc/tvm_ffi Exit 2。
  - `build-wheel.sh`：/opt/conda/bin/python -m build --wheel
    --no-isolation --outdir $DIST_DIR（默认 /workspace/dist）；不要求 .so。
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-2.1: 两脚本 bash -n 通过；grep 无 /builder、chaos/ai。
  - `rule` TR-2.2: build-native.sh 含 -I tvm_ffi/include 与 -ltvm_ffi；
    site-packages 用解释器动态获取不写死版本路径。
  - `rule` TR-2.3: 真实运行后 .so 生成且 readelf -d 含 tvm_ffi/lib rpath。

## Task 3: smoke 双脚本 + 内核注册
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `_toolchain_guards.py`：base GIL ABI 子进程断言、clang/patchelf/gdb
    走 PATH、import tvm_ffi、libtvm_ffi.so 与 tvm_ffi.h 存在、builder
    资产清单；subprocess 列表参数。
  - `smoke_native.py`：挂载点断言；.so 存在则 FfiBridge（PYTHONPATH=src）
    backend=native + 固定输入对照 `_reference_score_opportunity`
    容差 1e-9；.so 缺席跳过原生段 exit 0。
  - `scripts/register-kernel.sh`：agent-monetize-dev 内核 argv base
    python + env(PYTHONPATH src、LD_LIBRARY_PATH tvm_ffi/lib)，root+
    devuser 断言。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: py_compile/bash -n 过；无 shell=True/内嵌双引号 -c。
  - `rule` TR-3.2: 挂载断言独立于 libtvm 分支（缺席不掩盖挂载失败）。
  - `rule` TR-3.3: native 分支断言 backend==native 且数值容差通过。

## Task 4: Containerfile.agent-monetize
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - ARG BASE_IMAGE/PIP_MIRROR；Layer apt(clang/patchelf/gdb)→COPY builder
    + pip(apache-tvm-ffi==0.1.13.post3/PyYAML/build/wheel/setuptools/
    ipykernel/pytest/ruff)→COPY smoke/scripts→register-kernel+root/devuser
    守卫+横幅；无 SHELL/HEALTHCHECK/USER/ENTRYPOINT 覆盖；
    .dockerignore（**用 `**/__pycache__/` 嵌套模式**，技能 G7）+
    末层 find 清 pyc 双保险；LABEL。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 真实构建退出 0；守卫双身份 PASS；无 Healthcheck、
    入口 tini 链。
  - `rule` TR-4.2: 镜像内 pyc/__pycache__=0；apache-tvm-ffi pin 正确。

## Task 5: invoke monetize.* 八任务 + 注册
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 用 namespace 骨架渲染 `tasks/monetize.py`：
  PROJECT=agent-monetize-dev/SVC=monetize/前缀 MONETIZE/端口 2224/8892；
  单 _SOURCE_MOUNTS（MONETIZE_SRC_PATH→apps/agent-monetize）；8 任务
  （含 build-native/wheel 的 compose exec、smoke 双脚本顺序、BASE_PYTHON
  固定 /opt/conda/bin/python）；__init__.py import/Collection/configure/
  docstring（六命名空间）。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-5.1: invoke --list 8 任务；py_compile 过；无 import podman。
  - `rule` TR-5.2: Windows 原生 Exit 1；SRC 不存在 Exit 1 指引。

## Task 6: agent-monetize 源码 3 处跨平台适配
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - config.py：FFI native_lib 默认按 sys.platform（win→.dll/linux→.so/
    darwin→.dylib）；显式值优先。
  - config.yaml：native_lib 键置空/平台中立，使代码默认生效。
  - tests/test_ffi.py：NATIVE_LIB 平台分支；保留 reference/降级用例。
  - 不改 build.ps1、打分逻辑、其他文件。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-6.1: git diff 仅 3 文件；Windows .dll 分支字面仍在。
  - `rule` TR-6.2: 容器内 pytest tests/test_ffi.py 平台无关用例通过；
    Linux 下默认 native_lib 解析为 .so。

## Task 7: 规则/README/路由登记
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 新建 .agents/rules/monetize-overlay.md（技能红线 +
  apt clang/单一 GIL/tvm-ffi rpath/3 适配边界/.so 不入 wheel）；client
  AGENTS（命名空间数→六、overlay 行、路由树/表、规范入口、C13、
  CHANGELOG）、.agents/README（rules 5→6、资产/对应表/changelog）、
  root .env.example monetize 段、client README §14、apps/AGENTS 路由行；
  overlay README（FR-10）。
- **Acceptance Criteria Addressed**: AC-12, AC-14
- **Test Requirements**:
  - `rule` TR-7.1: 相对链接可达；任务名/端口/键三处一致。
  - `rule` TR-7.2: 白名单外 0 改动；onnx/xmnn/quant 零改。

## Task 8: 静态门禁汇总
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**: py_compile/bash -n、AC-1 grep、config 断言、
  invoke --list、Windows 门禁、键集合 diff、md 链接、白名单。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-11, AC-12
- **Test Requirements**:
  - `rule` TR-8.1: 全部静态检查退出 0 并归档输出。

## Task 9: 真实镜像构建取证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**: machine 内 podman build（aliyun pip）；观察 apt clang
  与 apache-tvm-ffi pip；守卫双身份；inspect；pyc=0；ABI/tvm_ffi。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-9.1: 构建退出 0，AC-3/4 断言逐项日志佐证。

## Task 10: build-native + 原生编译取证（AC-6）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 9
- **Description**: up（端口/挂载/kernel AC-5）→ exec build-native.sh
  真实 clang++ 编译；.so + readelf rpath。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-10.1: .so 生成；readelf -d rpath 含 tvm_ffi/lib；
    2224/8892、挂载、kernel 双可见取证。

## Task 11: native backend 冒烟（AC-7）+ wheel（AC-8）+ 源码零改
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 10
- **Description**: smoke_native root/devuser（backend=native + 数值
  容差）；build-wheel.sh 出 wheel；临时 venv（剥离 PYTHONPATH）装 wheel
  reference backend 验证 + venv 清理；agent-monetize git diff 仅 3 文件；
  pytest test_ffi 平台无关用例。
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-11.1: native 数值与参考一致；wheel 名/标签符合；venv 清理；
    diff 白名单。

## Task 12: 清理幂等、零侵入、收尾证据
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: down 保卷/两轮幂等/--volumes；bind/wheel 保留；
  白名单；quant/xmnn 门禁零回归；汇总证据入本文件。
- **Acceptance Criteria Addressed**: AC-10, AC-12
- **Test Requirements**:
  - `rule` TR-12.1: 计数断言全过；证据可复查。

## Task 13: fresh-context 独立审查
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 12
- **Description**: review.md 覆盖 AC-1~14 的 rule/rubric checkpoint；
  委托 fresh context；actionable 修复后复审。
- **Test Requirements**:
  - `rule` TR-13.1: 每 AC 有独立证据；rule 全 pass、rubric ≥4 才 finish。

---

# 完成证据汇总（2026-09-14）

- **静态（AC-1/2/11）**：py_compile/bash -n 全过；功能性文件禁项 grep 0；podman-compose config rc=0（2 bind 长语法+三必需+bridge+2224/8892）；invoke --list 8 任务；Windows monetize.ps Exit 1 双路径；镜像渲染自脚手架模板（dogfood，占位符 0 残留）。
- **镜像（AC-3/4）**：基底曾因 machine 存储重置丢失，从 `jupyter-podman-rootless/.image-cache/latest.tar.gz` load 恢复；构建 `localhost/agent-monetize-dev:latest`=**666b60ac2e88（1.67GB，xmnn-dev 4.43GB 的 38%，验证轻量变体）**，root+devuser 守卫 PASS；pyc=0；base 3.14.7 GIL=True + tvm_ffi 0.1.13，main 3.14.7 Py_GIL_DISABLED=1。
- **AC-5**：栈 Up 后 /workspace/agent-monetize/src/agent_monetize 可见、kernelspec agent-monetize-dev 双可见、lab HTTP 302（60s 窗口取证）。
- **AC-6**：build-native.sh clang++ 一次编译成功，score_opportunity.so 88K，NEEDED libtvm_ffi.so，RUNPATH=/opt/conda/lib/python3.14/site-packages/tvm_ffi/lib（Q2 绝对 rpath 成立）。
- **AC-7（核心）**：单次 exec 串行（规避环境窗口），backend=native、load_error=None、native_lib_path=挂载 .so；固定输入 native=6.068041758 与 reference **diff=0.000e+00**；root 与 devuser 双 PASS；test_ffi.py pytest **9/9**。
- **AC-8**：setuptools 出 `agent_monetize-0.1.0-py3-none-any.whl`（40K，30 项，无 .so）；run --rm 隔离 venv（--system-site-packages，剥 PYTHONPATH）装 wheel 后 import + reference score=6.068042 通过，venv 随容器清理。
- **AC-9**：git status agent-monetize 恰好 3 文件 M（config.py/config.yaml/test_ffi.py）；build.ps1 零改动且保留 2 处 .dll；config.py 平台函数 win/darwin/linux 三分支 + from_dict 空值回退。
- **AC-10**：down 后项目容器计数 0；wheel/源码 bind 保留。
- **AC-12**：monetize 全部改动在白名单；onnx overlay/quant.py 零改；xmnn.py 的 M 属上会话 dcbf03fbb 之前遗留（本任务未触碰）。
- **环境限制（非栈缺陷，已在取证中规避）**：machine 当前 runRoot=/mnt/wslg/runtime-dir（tmpfs），detached 容器约 40-60s 后被会话回收（FinishedAt 零值/OOM=false/前台 run 常驻稳定）；运行态取证改用「up 后单次 exec 串行」与「run --rm 前台」完成，镜像/脚本/产物正确性不受影响。建议后续单独排查 machine linger/runroot 持久化。
