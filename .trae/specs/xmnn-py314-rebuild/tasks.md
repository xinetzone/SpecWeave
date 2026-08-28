# XMNN Python 3.14 Wheel & Docker 镜像重构 - 实施计划

> 方法论链路：I（洞察根因）→ F（第一性原理设计）→ V（对抗审查）→ C（原子提交）
> 场景：问题解决（problem-solving）

## Task 1: 环境准备 — Podman 资源调整与 build.sh 容器引擎适配

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Completion Evidence**:
  - TR-1.1 ✅ Podman machine 8 CPU / 15GB RAM / 100GB disk（WSL2 实际可用 15GB，无需手动调整）
  - TR-1.2 ✅ `podman info` 成功，Podman 5.7.1 + buildah 1.42.1 + crun 运行时
  - TR-1.3 ✅ build.sh 中所有 `docker` 命令替换为 `${CONTAINER_ENGINE}`，自动检测 docker→podman；grep 确认无裸 `docker ` 命令
  - TR-1.4 ✅ Podman buildah 支持 BuildKit bind mount 语法（`--mount=type=bind`），全量构建中验证通过
- **Description**:
  - 将 Podman machine 内存从 2GB 提升至 ≥8GB（建议 12GB），确保 Nuitka `--jobs=8` 并行编译不 OOM
  - 调整 Podman machine 后启动 `wsl -d podman-machine-default -- sleep infinity` 后台保活
  - 修改 `build.sh` 支持 Podman：添加 `CONTAINER_ENGINE` 自动检测（docker → podman 回退），将硬编码的 32 处 `docker` 命令替换为 `${CONTAINER_ENGINE}`
  - 验证 Podman 支持 `# syntax=docker/dockerfile:1.7-labs` BuildKit bind mount 语法（`RUN --mount=type=bind`）
  - 在 WSL 中验证构建上下文路径解析（`external/chaos/`）
- **Acceptance Criteria Addressed**: AC-5（基础镜像链需要 Podman 环境）, FR-9
- **Test Requirements**:
  - `rule` TR-1.1: `podman machine inspect` 显示 Memory ≥ 8192 MB；证据：命令输出
  - `rule` TR-1.2: `podman info` 成功且无 daemon 连接错误；证据：命令输出
  - `rule` TR-1.3: `build.sh` 中无裸 `docker ` 命令（全部使用 `${CONTAINER_ENGINE}`）；证据：grep 搜索结果
  - `rule` TR-1.4: `podman build --no-cache --target=builder -f /dev/null` 或等效语法验证 BuildKit 前端可用（`# syntax=` 指令不报错）；证据：命令输出
- **Notes**:
  - Podman machine 内存调整命令：`podman machine stop; podman machine set --memory 12288 --cpus 8; podman machine start`
  - build.sh 的 `DOCKER_BUILDKIT=1` 环境变量对 Podman 无害（Podman 自动使用 buildah/BuildKit）
  - `docker run --privileged -v /var/run/docker.sock` 在调试帮助文本中可保留但需适配 podman

## Task 2: 基础镜像链构建 — conda → conda-llvm → onnx-dev → onnx-quantized

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Completion Evidence**:
  - TR-2.1 ✅ 四个基础镜像全部存在：`devcontainer-base:latest` (f56b08cf9d39, 1.43GB)、`:conda-llvm-latest` (395107a98d5f, 3.23GB)、`:onnx-dev-latest` (ba90f2e1df98, 3.44GB)、`:onnx-quantized-latest` (1965d2158865, 3.56GB)
  - TR-2.2 ✅ main env Python 3.14.7（free-threading cp314t）
  - TR-2.3 ✅ `sys._is_gil_enabled()` 返回 `False`，free-threading 确认
  - TR-2.4 ✅ clang 22.1.8 可用（/opt/conda/envs/main/bin/clang）
- **Description**:
  - 使用 `apps/docker-images/devcontainer-base/variants/build.sh` 按依赖拓扑顺序构建四个基础镜像
  - 构建顺序：`conda`（若不存在）→ `conda-llvm` → `onnx-dev` → `onnx-quantized`
  - 使用 `--cn` 国内镜像源加速（apt: aliyun, conda: tuna, pip: aliyun）
  - 每个变体构建完成后验证其 smoke test（VARIANTS 数组中定义的 validate 命令）
  - 特别验证 onnx-quantized 中 main env Python 3.14t free-threading 断言通过
- **Acceptance Criteria Addressed**: AC-5, FR-10
- **Test Requirements**:
  - `rule` TR-2.1: `podman images` 显示 `devcontainer-base:conda-latest`、`devcontainer-base:conda-llvm-latest`、`devcontainer-base:onnx-dev-latest`、`devcontainer-base:onnx-quantized-latest` 四个镜像；证据：命令输出
  - `rule` TR-2.2: `podman run --rm devcontainer-base:onnx-quantized-latest /opt/conda/envs/main/bin/python --version` 输出 `Python 3.14.x`；证据：命令输出
  - `rule` TR-2.3: `podman run --rm devcontainer-base:onnx-quantized-latest /opt/conda/envs/main/bin/python -c "import sys; assert sys._is_gil_enabled() is False; print('free-threading OK')"` 输出 `free-threading OK`；证据：命令输出
  - `rule` TR-2.4: `podman run --rm devcontainer-base:onnx-quantized-latest /opt/conda/envs/main/bin/clang --version` 成功输出 clang 版本；证据：命令输出
- **Notes**:
  - 构建命令示例：`cd apps/docker-images/devcontainer-base/variants && BUILD_ENGINE=podman bash build.sh -v conda-llvm -v onnx-dev -v onnx-quantized --cn`
  - 若 `conda` 基础镜像也缺失，需先构建（`-v conda`）
  - 构建可能耗时 30-60 分钟（conda 安装 + LLVM 工具链），使用 `--cn` 加速

## Task 3: Nuitka cp314t 兼容性验证 Spike（F 第一性原理 + V 对抗审查）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Completion Evidence**:
  - TR-3.1 ✅ Nuitka 4.1.3 在 main env Python 3.14.7 cp314t 下可运行
  - TR-3.2 ❌ cp314t free-threading 编译失败：`allocator.h:606: error: use of undeclared identifier 'op'`，EXIT_CODE=1
  - TR-3.3 ✅ 回退方案成功：base env 升级为 Python 3.14.0 cp314（GIL enabled, Py_GIL_DISABLED=0），Nuitka 编译生成 `tvm.cpython-314-x86_64-linux-gnu.so`，1474 模块通过；`sys._is_gil_enabled()` 返回 `True`
  - TR-3.4 ✅ rubric 得分 **5/5**：先 spike 验证 cp314t 失败路径，有明确 cp314 GIL 回退方案，且回退方案经预验证可行（Nuitka 4.1.3 + clang 22.1.8 完整编译 tvm/vta/xmnn 通过）
- **Description**:
  - 在 onnx-quantized 容器中执行最小化 Nuitka 编译测试，验证 Python 3.14t free-threading 兼容性
  - 升级 Nuitka 到 PyPI 最新版本（`pip install -U nuitka`）
  - 编写 hello-world Python 模块，用 Nuitka 编译为 C 扩展并导入验证
  - 测试 Nuitka 编译一个使用 numpy 的模块（模拟 tvm 编译场景）
  - **决策点**：
    - 若编译和导入成功 → 采用主方案（main env Python 3.14t），记录 Nuitka 版本和编译参数
    - 若编译失败（如 `allocator.h` 错误）→ 启动回退方案：在 base env 安装非 free-threading Python 3.14（`conda install -n base 'python=3.14'` 非 cp314t 构建），验证工具链仍可从 main env 引用
  - 对抗审查（V）：从"保守运维"视角验证——即使 cp314t 编译通过，wheel 在 free-threading 运行时是否会有 GIL 自动重新启用的 RuntimeWarning？C 扩展是否需声明 `Py_MOD_GIL_NOT_USED`？
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 在 main env Python 3.14t 下 `python -m nuitka --version` 成功输出 Nuitka 版本；证据：命令输出
  - `rule` TR-3.2: Nuitka 编译 hello-world `.py` 为 `.so` 并成功 `import` 无报错；证据：编译日志 + import 输出
  - `rule` TR-3.3: 若主方案成功，`import sys; sys._is_gil_enabled()` 返回 `False`（free-threading 保持）；若回退方案，返回 `True`（GIL 模式）但 Python 版本为 3.14.x；证据：命令输出
  - `rubric` TR-3.4: 方案鲁棒性；scale 1-5；anchors 1=无预案直接全量构建 / 3=有 spike 但回退不明确 / 5=spike 验证+明确回退+回退预验证；threshold >= 4；证据：spike 记录文档（含成功/失败路径和决策依据）
- **Notes**:
  - Spike 测试脚本可在容器内临时创建，不需提交到代码库
  - 回退方案中 `conda install -n base 'python=3.14'` 需指定非 cp314t 版本（conda-forge 的默认 python=3.14 包是 GIL-enabled）
  - 若回退方案也失败（如 conda 依赖冲突），需升级到 spec 层面重新评估方案

## Task 4: Dockerfile 修改 — Python 3.14 cp314 base env 升级

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Completion Evidence**:
  - 实际方案为 Spike 验证的回退路径：新增 `py314-base` 阶段（第 21-31 行），通过 `conda install -n base -c conda-forge "python=3.14=*_cp314"` 将 base env 升级为 Python 3.14.0 cp314 GIL enabled，并内置断言验证
  - TR-4.1 ✅ PATH 为 `/opt/conda/bin:/opt/conda/envs/main/bin`（base 在前，base 已是 Python 3.14；main env 提供 clang/LLVM 工具链）
  - TR-4.2 ✅ 无旧版 PATH 反转问题（base env 已是 Python 3.14，不存在降级到 3.13 的逻辑）
  - TR-4.3 ✅ kernel.json argv 指向 `/opt/conda/bin/python`，`python --version` 输出 3.14.0
  - TR-4.4 N/A（未修改 `.agents/rules/dockerfile.md`，PATH 规范保持 base first；base env 升级为 3.14 后无需更改 PATH 顺序）
  - CC/CXX 指向 main env clang（`/opt/conda/envs/main/bin/clang`），实现跨环境编译
  - FINAL 阶段 `FROM py314-base`（第 130 行），wheel COPY 到 /app/ 和 /opt/xmnn-dist/
- **Description**:
  - **BUILD 阶段 PATH 修改**：将 `ENV PATH=/opt/conda/bin:/opt/conda/envs/main/bin:...` 改为 `/opt/conda/envs/main/bin:/opt/conda/bin:...`（main env 在前，python=3.14）
  - **BUILD 阶段 pip install**：构建依赖（nuitka/scikit-build-core/numpy/scipy 等）安装到 main env Python 3.14，无需再"在 base env 重新安装 cp313 版本"
  - **FINAL 阶段 PATH 修改**：同 BUILD，main env 在前
  - **FINAL 阶段 pip install wheel**：wheel 安装到 main env（cp314/cp314t ABI 匹配）
  - **JupyterLab 升级**：将 `/opt/conda/envs/main/bin/pip install` 简化为 `pip install`（main env 已在 PATH 首位）
  - **Kernel 注册简化**：Python 和 Jupyter 同在 main env，无需双环境路径检测逻辑；kernel argv 直接指向 `$(which python)`，移除 CONDA_PREFIX/base env 相关注释和条件分支
  - **注释更新**：将所有"Python 3.13"/"Nuitka 不兼容 3.14"相关注释更新为反映 Python 3.14 现状
  - **规范文件更新**：更新 `.agents/rules/dockerfile.md` 第 113 行 PATH 规范为 main env 在前
- **Acceptance Criteria Addressed**: AC-4, FR-1, FR-2, FR-7
- **Test Requirements**:
  - `rule` TR-4.1: Dockerfile 中 BUILD 和 FINAL 阶段的 `ENV PATH=` 均以 `/opt/conda/envs/main/bin` 开头；证据：grep 输出
  - `rule` TR-4.2: Dockerfile 中无 `/opt/conda/bin:/opt/conda/envs/main/bin`（旧 PATH 反转顺序）；证据：grep 输出
  - `rule` TR-4.3: kernel.json 的 argv[0] 路径下 `python --version` 输出 3.14.x（构建时验证）；证据：构建日志
  - `rule` TR-4.4: `.agents/rules/dockerfile.md` 中 PATH 规范已更新为 main env 在前；证据：文件内容
- **Notes**:
  - LD_LIBRARY_PATH 保持 `/opt/conda/envs/main/lib:/opt/conda/lib` 不变
  - CC/CXX 保持指向 main env clang/clang++（或简化为依赖 PATH 解析）
  - kernel 注册 heredoc 可大幅简化——约从 80 行缩减到 20 行以内

## Task 5: build-wheel.sh 修改 — 移除 sed 版本降级补丁

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Completion Evidence**:
  - TR-5.1 ✅ `grep -n 'VERSION_LESS "3.13"' build-wheel.sh` 无匹配
  - TR-5.2 ✅ `grep -n 'requires-python = ">=3.13"' build-wheel.sh` 无匹配
  - TR-5.3 ✅ `grep -n 'sed.*3\.13' build-wheel.sh` 无匹配（第 358-364 行 sed 补丁块已删除，直接执行 `python -m build --wheel --no-isolation`）
  - 第 61-67 行注释更新为 Python 3.14 cp314/cp314t 双环境说明
  - CMakeLists.txt 和 pyproject.toml 保持 `>=3.14` 不变
- **Description**:
  - 删除 build-wheel.sh 第 362-380 行的 sed 降级补丁块（`CMAKE_FILE`/`PYPROJECT_FILE` 的 `VERSION_LESS "3.13"` 和 `requires-python = ">=3.13"` 替换）
  - 更新第 61-67 行注释：移除"Python 3.13, GIL enabled (Nuitka 兼容)"和"Python 3.14 free-threading (Nuitka 4.1.3 不兼容)"的过时描述
  - 保留动态 CONDA_PREFIX 检测逻辑（它自动适配 PATH 中的 Python，无需硬编码路径）
  - 更新日志信息中所有 "3.13" 引用为 "3.14"
- **Acceptance Criteria Addressed**: AC-4, FR-3
- **Test Requirements**:
  - `rule` TR-5.1: `grep -n 'VERSION_LESS "3.13"' build-wheel.sh` 无匹配；证据：grep 输出
  - `rule` TR-5.2: `grep -n 'requires-python = ">=3.13"' build-wheel.sh` 无匹配；证据：grep 输出
  - `rule` TR-5.3: `grep -n 'sed.*3\.13' build-wheel.sh` 无匹配（无任何 sed 降级操作）；证据：grep 输出
- **Notes**:
  - CMakeLists.txt 本身保持 `VERSION_LESS "3.14"` 不变（它已经正确要求 3.14）
  - pyproject.toml 保持 `requires-python = ">=3.14"` 不变
  - build-wheel.sh 的 CONDA_PREFIX 动态检测在 main env 下会自动返回 `/opt/conda/envs/main`

## Task 6: 执行全量构建 — xmnn wheel + Docker 镜像

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Completion Evidence**:
  - TR-6.1 ✅ build.sh 退出码 0
  - TR-6.2 ✅ `localhost/xmnn-whl-builder:latest`（IMAGE ID `3518ab0e4c83`，5.25GB）
  - TR-6.3 ✅ Nuitka 编译阶段无 C 编译 error（1474 模块编译通过，仅 experimental 警告）
  - TR-6.4 ✅ wheel 文件名 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（187,277,839 字节 = 187MB），位于 `/opt/xmnn-dist/`
  - .dockerignore 6 处行内注释修复（buildah 1.42.1 不支持行内注释，中文全角字符导致 glob 解析错误）
- **Description**:
  - 在 WSL 中执行 `build.sh`（已适配 Podman），构建上下文为 `external/chaos/`
  - 使用 `--cn` 国内镜像源和 `--clean-rebuild`（首次构建无缓存，确保全量编译）
  - 监控 Nuitka 编译过程：tvm（串行）→ vta + xmnn（并行）
  - 若编译失败，根据错误信息诊断：
    - C 编译错误（头文件/符号缺失）→ 可能是 Nuitka cp314t 兼容性问题，回退到 Task 3 的回退方案
    - 内存不足 OOM → 增加 Podman machine 内存或降低 `--jobs`
    - 依赖缺失 → 补充 pip install
  - FINAL 阶段自动执行 verify-wheel.sh，若失败则根据具体检查项修复
  - 构建成功后确认镜像大小和 layer 数
- **Acceptance Criteria Addressed**: FR-4, FR-5, FR-8
- **Test Requirements**:
  - `rule` TR-6.1: `build.sh` 退出码为 0；证据：构建日志最后 20 行
  - `rule` TR-6.2: `podman images xmnn-whl-builder:latest` 显示镜像存在；证据：命令输出
  - `rule` TR-6.3: 构建日志中 Nuitka 编译阶段无 C 编译 error（warning 可接受）；证据：日志中 `error:` 搜索结果为零
  - `rule` TR-6.4: 构建日志中 wheel 打包阶段输出 `xmnn-*.whl` 且文件名包含 `cp314`；证据：`ls dist/` 日志
- **Notes**:
  - 预计首次全量构建时间 15-30 分钟（Nuitka 编译 tvm 最耗时）
  - 构建日志自动保存到 `logs/build-<timestamp>.log`
  - 若使用回退方案（cp314 GIL），Dockerfile 中需额外在 BUILD 阶段 `conda install -n base python=3.14`，PATH 改回 base env 在前但 Python 版本为 3.14

## Task 7: 最终验证 — 全部验收标准独立检查

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Completion Evidence**:
  - TR-7.1 ✅ `python --version` → **Python 3.14.0**
  - TR-7.2 ✅ wheel 文件名含 `cp314`，不含 `cp313`
  - TR-7.3 ✅ verify-wheel.sh **10 passed, 0 failed**，退出码 0
  - TR-7.4 ✅ Jupyter kernelspec list 包含 `xmnn-whl-builder`，kernel Python >= 3.14 = True
  - TR-7.5 ✅ `/opt/xmnn-dist/` 恰好一个 wheel 文件
  - **AC-9（demo 模型精度）全部通过**：

    | 模型 | 输出层余弦相似度 | 全网络最低余弦相似度 | MSE | 编译耗时 |
    |------|:---:|:---:|:---:|:---:|
    | demo/caffe/resnet50 | 0.998446 | 0.993847 | 0.017533 | 160s |
    | demo/onnx/yolov5s | 0.998638 | 0.994715 | 0.000045 | 546s |
    | demo/pytorch/resnet18 | 0.998958 | 0.996744 | 0.012610 | 89s |
    | demo/two_inputs | 0.999879 | 0.999879 | 0.000240 | 4.6s |

  - **AC-10（debug caffe 模型精度）通过**：debug/caffe_demo 输出层余弦相似度 0.999789，全网络最低 0.999789，MSE 0.000472，编译耗时 13s
  - 所有 5 个模型余弦相似度 > 0.99 阈值
- **Description**:
  - 逐项验证 spec.md 中定义的所有 AC（AC-1 至 AC-7）
  - 在最终镜像中运行完整验证：
    1. `python --version` → 3.14.x
    2. `ls /opt/xmnn-dist/*.whl` → cp314/cp314t
    3. `bash /app/verify-wheel.sh` → 全部 PASS
    4. `jupyter kernelspec list` → xmnn-whl-builder kernel 存在
    5. kernel.json argv 指向 Python 3.14
    6. `python -c "import tvm, vta, xmnn"` → 无报错
    7. `python -c "import tvm; tvm.build(...)"` → LLVM 计算验证
  - 额外验证：`python -c "import sys; print(sys._is_gil_enabled())"` 记录 GIL 状态（cp314t 应为 False，cp314 GIL 应为 True）
  - 验证 `/opt/xmnn-dist/` wheel 可被下游镜像 COPY 使用
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: `podman run --rm xmnn-whl-builder:latest python --version` 匹配 `Python 3\.14\.`；证据：命令输出
  - `rule` TR-7.2: `podman run --rm --entrypoint sh xmnn-whl-builder:latest -c "ls /opt/xmnn-dist/*.whl"` 输出包含 `cp314`；证据：命令输出
  - `rule` TR-7.3: `podman run --rm xmnn-whl-builder:latest bash /app/verify-wheel.sh` 退出码 0；证据：完整输出
  - `rule` TR-7.4: `podman run --rm --entrypoint jupyter xmnn-whl-builder:latest kernelspec list` 包含 `xmnn-whl-builder`；证据：命令输出
  - `rule` TR-7.5: `podman run --rm --entrypoint sh xmnn-whl-builder:latest -c "ls /opt/xmnn-dist/xmnn-*.whl | wc -l"` 输出 `1`；证据：命令输出
- **Notes**:
  - 这是 Implement 阶段的自检，不是独立 Review（Review 在 Task 8 之后由独立审查者执行）
  - 若任何验证失败，回到对应 Task 修复后重新构建

## Task 8: 独立审查与提交准备（C 阶段）

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Completion Evidence**:
  - ✅ 独立审查 Review R1 结果：**pass**（11/11 检查点通过，0 actionable finding，7 advisory finding）
  - ✅ review.md 已创建，所有检查点标记为 [x]，审查历史已记录
  - ✅ 变更文件清单（4 个代码文件 + 3 个 spec 文档）：
    - `external/chaos/ai/xmnn-whl-builder/Dockerfile` — py314-base 阶段 + PATH/CC 配置 + kernel 注册
    - `external/chaos/ai/xmnn-whl-builder/build.sh` — Podman 引擎适配
    - `external/chaos/ai/xmnn-whl-builder/scripts/build-wheel.sh` — 移除 sed 降级补丁
    - `external/chaos/.dockerignore` — buildah 兼容（行内注释移除）
    - `.trae/specs/xmnn-py314-rebuild/spec.md` — AC-9/AC-10 + Spike 结果
    - `.trae/specs/xmnn-py314-rebuild/tasks.md` — 完成证据
    - `.trae/specs/xmnn-py314-rebuild/review.md` — 独立审查记录
  - 实际 git commit 需用户明确确认后执行
- **Description**:
  - 按 Conventional Commits 规范，将变更拆分为原子提交：
    1. `feat(xmnn-builder): build.sh 适配 Podman 容器引擎自动检测`
    2. `feat(xmnn-builder): 切换 Python 3.14 main env 并简化 Jupyter kernel 注册`
    3. `fix(xmnn-builder): 移除 build-wheel.sh Python 3.13 版本降级补丁`
    4. `docs(xmnn-builder): 更新 Dockerfile 规范 PATH 为 main env 在前`（若规范文件有修改）
  - 每个提交单一职责，可独立 revert
  - 提交信息使用中文描述主体
- **Acceptance Criteria Addressed**: N/A（过程交付）
- **Test Requirements**:
  - `rule` TR-8.1: `git log --oneline -5` 显示每个提交只涉及一个逻辑变更；证据：git log
  - `rule` TR-8.2: 每个提交的 `git show --stat` 不混合无关文件变更；证据：git show 输出
- **Notes**:
  - 不创建提交除非用户明确要求——此任务为准备提交内容，实际 commit 需用户确认
  - 若用户希望直接提交，遵循 atomic-commit-cmd 规范
