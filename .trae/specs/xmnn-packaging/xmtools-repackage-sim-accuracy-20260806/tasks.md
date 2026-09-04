# xmtools 重新打包 + hub/caffe+onnx 仿真精度测试 - The Implementation Plan

## [ ] Task 1: WSL 环境预检与构建准备
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 WSL 中确认 Docker daemon 运行中（`docker --version`、`docker ps`）
  - 确认 `/mnt/d/spaces/SpecWeave` 可访问，`external/chaos/xmtools`、`external/chaos/npu_tvm`、`external/chaos/npuusertools` 三个目录完整
  - 确认 `xmnn-dev:llvm22` 开发镜像存在（`docker images xmnn-dev:llvm22`），如不存在则需要先构建
  - 清理 `xmtools/dist/` 目录中的旧 wheel 文件（如有），确保本次构建产物唯一
  - 创建 `xmtools/build/` 目录（用于存放日志、备份、报告）
- **Acceptance Criteria Addressed**: AC-1 (前置环境)
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker --version` 正常输出，`docker ps` 无错误
  - `programmatic` TR-1.2: 三个兄弟目录（xmtools、npu_tvm、npuusertools）均存在且非空
  - `programmatic` TR-1.3: `docker images xmnn-dev:llvm22` 能列出镜像（或记录需先构建）
  - `programmatic` TR-1.4: `xmtools/build/` 目录已创建
- **Notes**: 若 `xmnn-dev:llvm22` 不存在，需先在 WSL 中执行 `cd docker/dev-llvm22 && bash build-docker.sh` 构建开发镜像（耗时约10-20分钟）

## [ ] Task 2: 在 WSL Docker 中重新打包 xmnn wheel
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 WSL 中进入 `external/chaos/xmtools/docker/dev-llvm22/` 目录
  - 执行 `bash build-and-test.sh --no-build`（复用已存在的 `xmnn-dev:llvm22` 镜像，不重新构建镜像）
  - 该脚本会：patch pyproject.toml → Nuitka 编译 vta → Nuitka 编译 xmnn → `python -m build --wheel --no-isolation` → 恢复 pyproject.toml → auditwheel show → 快速 sanity check
  - 构建成功后确认 `dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 存在
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: `build-and-test.sh --no-build` 以 exit code 0 结束
  - `programmatic` TR-2.2: `dist/` 目录下存在且仅存在一个 `xmnn-*-cp314-cp314-linux_x86_64.whl` 文件
  - `programmatic` TR-2.3: wheel 大小在合理范围内（~160-200MB）
  - `programmatic` TR-2.4: 构建日志中 sanity check 输出 `tvm.build(llvm) compute test: PASS`
  - `programmatic` TR-2.5: pyproject.toml 已恢复（无 `#cmake.version` 注释残留）
- **Notes**: Nuitka 编译 vta + xmnn 约需 5-15 分钟（取决于缓存）。若构建失败，收集错误日志并排查（常见原因：LLVM版本不一致、Nuitka 版本问题、源码路径错误）

## [ ] Task 3: 基于新 wheel 构建运行时 Docker 镜像
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 WSL 中进入 `external/chaos/xmtools/docker/runtime/` 目录
  - 确认 `miniconda.sh` 存在（如不存在从 `../dev-llvm22/` 复制）
  - 执行 `bash build-runtime.sh -t xmnn:1.2.1-sim-accuracy`
  - 该脚本会：检查 wheel → 复制 miniconda.sh 和 wheel 到构建上下文 → `docker build` → 清理临时文件
  - Dockerfile 内会执行 `verify_xmnn.py` 作为构建最后一步（RUN 指令），若验证失败则镜像构建失败
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: `build-runtime.sh -t xmnn:1.2.1-sim-accuracy` 以 exit code 0 结束
  - `programmatic` TR-3.2: `docker images xmnn:1.2.1-sim-accuracy` 能列出新镜像
  - `programmatic` TR-3.3: `docker run --rm xmnn:1.2.1-sim-accuracy` 输出 XMNN runtime ready 信息且无错误
- **Notes**: 运行时镜像不包含 LLVM/CMake/Ninja 等构建工具，体积约 1.5-2GB（含 conda Python + xmnn wheel + 依赖）

## [ ] Task 4: 扩展 patch_to_sim.py 支持 hub/caffe 和 hub/onnx
- **Priority**: high
- **Depends On**: Task 1 (可并行准备，不依赖 wheel 构建)
- **Description**:
  - 当前 `docker/runtime/patch_to_sim.py` 的 `GROUPS = ["debug", "demo", "tests"]`，需要扩展为 `["hub/caffe", "hub/onnx"]` 或修改为支持 hub 子目录
  - 脚本需在 `[compile]` 段内正确匹配和替换 `target = ...` 和 `tune = ...`
  - 兼容已设置为 `sim_vta2.0` 的模型（替换后内容不变不算变更）
  - 同时编写/确认 `backup_configs.sh` 能备份 hub/caffe 和 hub/onnx 的所有 config.toml
  - 备份目标为 `build/hub_config_backup/`，保持相对目录结构
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 修改后的 patch 脚本能正确遍历 hub/caffe 和 hub/onnx 下所有 config.toml（包括嵌套子目录如 car_model/adas/lane_road）
  - `programmatic` TR-4.2: patch 后所有 config.toml 的 `[compile]` 段内 `target` 值为 `"sim_vta2.0"`，`tune` 值为 `false`
  - `programmatic` TR-4.3: 原本已是 sim_vta2.0 的模型 patch 后内容不变（不产生无意义变更）
  - `programmatic` TR-4.4: backup 脚本备份的文件数等于 hub/caffe + hub/onnx 下 config.toml 的总数
  - `human-judgment` TR-4.5: 脚本代码审查——正则表达式正确匹配 `[compile]` 段内字段，不误改其他段的同名字段
- **Notes**: 可以修改 GROUPS 列表为 `["hub/caffe", "hub/onnx", "debug", "demo", "tests"]` 以保持向后兼容，也可以单独为 hub 编写新脚本。建议在 MODELS_ROOT 下按组递归查找，使用 `rglob("config.toml")`。注意 hub 下有嵌套子目录（如 onnx/car_model/adas/lane_road/）

## [ ] Task 5: 创建批量编译与精度测试编排脚本
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 在 `docker/runtime/` 下创建 `run_hub_sim_tests.py`（或 bash 脚本），负责：
    1. 读取 `enumerate_hub.py` 输出的模型清单（`/tmp/hub_models_list.txt`）
    2. 逐模型执行 `python -m sdk.tools.compile -n <model_name>`，记录 exit code、stdout/stderr 到 `build/compile_logs/<model_name>.log`
    3. 编译成功的模型记录到 `build/compile_success.txt`，失败的记录到 `build/compile_failed.txt`（含错误摘要）
    4. 对编译成功的模型逐模型执行 `python -m sdk.tools.accuracy -n <model_name>`，记录 exit code、stdout/stderr 到 `build/accuracy_logs/<model_name>.log`
    5. 精度测试成功后复制模型目录下的 `result.csv` 到 `build/accuracy_results/<model_name>/result.csv`
    6. 精度测试失败的模型记录到 `build/accuracy_failed.txt`
    7. 容错：单模型失败不中断，`set +e` 或 try/except 包裹
  - 脚本需在运行时容器内执行（通过 `docker run` 挂载 workspace）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 脚本能正确读取模型清单并逐模型调用 compile.py
  - `programmatic` TR-5.2: 单模型编译失败后脚本继续执行下一个模型
  - `programmatic` TR-5.3: 编译日志按模型名分类保存到 compile_logs/
  - `programmatic` TR-5.4: 编译成功模型列表 compile_success.txt 格式正确（每行一个模型名）
  - `programmatic` TR-5.5: 脚本对编译成功模型自动调用 accuracy.py
  - `programmatic` TR-5.6: result.csv 文件被收集到 build/accuracy_results/ 对应模型目录
  - `human-judgment` TR-5.7: 脚本结构清晰，日志包含时间戳，便于排查
- **Notes**: 预计编译 60 个模型需 30-60 分钟（每个模型约 30 秒到数分钟），精度测试额外需要时间。建议脚本输出进度信息（如 `[12/60] Compiling hub.caffe.palm...`）。注意模型名中的点号会映射为路径分隔符，需确保目录创建正确。

## [ ] Task 6: 备份 hub config.toml 并 patch 为仿真 target
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 在运行时容器挂载 workspace 后，或在 WSL 中直接执行：
  1. 创建备份目录 `build/hub_config_backup/`
  2. 备份所有 hub/caffe 和 hub/onnx config.toml 到备份目录（保持相对路径结构）
  3. 执行扩展后的 patch_to_sim.py（或新脚本）批量设置 `compile.target = "sim_vta2.0"` 和 `compile.tune = false`
  4. 验证 patch 结果：抽查几个 config.toml 确认 target 和 tune 已正确设置
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 备份文件数量等于 hub/caffe + hub/onnx 下 config.toml 总数
  - `programmatic` TR-6.2: 随机抽查 5 个 config.toml（含嵌套子目录），确认 target 和 tune 已正确设置
  - `programmatic` TR-6.3: 没有误改 [model] 或 [inference] 等其他段的字段
- **Notes**: 此操作修改 models/hub/ 下的文件，测试结束后必须恢复（Task 10）

## [ ] Task 7: 枚举完整产物模型
- **Priority**: high
- **Depends On**: Task 3, Task 6
- **Description**:
  - 在运行时容器中执行 `python docker/runtime/enumerate_hub.py`
  - 确认 enumerate_hub.py 的 MODELS_ROOT 指向容器内 `/workspace/xmtools/models/hub`（容器内路径）
  - 收集输出，记录完整模型清单和不完整模型清单
  - 模型清单保存到 `build/hub_models_list.txt`
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: enumerate_hub.py exit code 0
  - `programmatic` TR-7.2: `/tmp/hub_models_list.txt`（或 build/hub_models_list.txt）包含完整模型名列表
  - `programmatic` TR-7.3: 清单中模型均为 frontend=caffe 或 frontend=onnx
  - `human-judgment` TR-7.4: 不完整模型清单合理（缺少模型文件或 dataset 的模型被正确识别）
- **Notes**: 上次会话枚举出 60 个完整模型（30 caffe + 30 onnx），1 个不完整（hub.onnx.car_model.track_all.test）

## [ ] Task 8: 执行批量编译
- **Priority**: high
- **Depends On**: Task 5, Task 7
- **Description**:
  - 在运行时容器中执行批量编译编排脚本
  - 容器启动命令示例：`docker run --rm -v /mnt/d/spaces/SpecWeave/external/chaos:/workspace -w /workspace/xmtools xmnn:1.2.1-sim-accuracy python docker/runtime/run_hub_sim_tests.py --compile-only`
  - 监控进度，等待所有模型编译完成
  - 汇总编译结果：成功数、失败数、失败原因分类
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有清单中的模型都被尝试编译（不遗漏）
  - `programmatic` TR-8.2: compile_success.txt 和 compile_failed.txt 均生成
  - `programmatic` TR-8.3: 编译成功模型的 network.xmnn 和 param.bin 存在于对应模型目录
  - `programmatic` TR-8.4: 编译失败模型的日志文件存在且包含错误信息
  - `programmatic` TR-8.5: 编译过程不因单个模型失败而中断（脚本容错）
- **Notes**: 预期部分模型可能因不支持的算子、OOM、配置错误等原因编译失败（上次有 11 个 FAIL），记录失败原因即可，本次任务不修复

## [ ] Task 9: 执行批量精度测试
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 对 compile_success.txt 中的所有模型执行精度测试
  - 使用编排脚本的精度测试模式：`python docker/runtime/run_hub_sim_tests.py --accuracy-only`（或自动接续编译阶段）
  - 每个模型执行 `accuracy.py -n <model_name>`，该 API 会加载模型、运行推理、对比参考输出，生成 result.csv
  - 收集 result.csv 到 build/accuracy_results/
  - 记录精度测试失败的模型及原因
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: compile_success.txt 中的所有模型都被尝试精度测试
  - `programmatic` TR-9.2: 每个精度测试成功的模型的 result.csv 被收集
  - `programmatic` TR-9.3: accuracy_failed.txt 记录失败模型及错误摘要
  - `programmatic` TR-9.4: result.csv 包含余弦相似度、MSE、MAE 等指标列
- **Notes**: 精度测试可能使用 config.toml 中 `[accuracy] input` 指定的输入图片。如果 accuracy.py 内部使用 dataset.txt 做校准并使用默认输入推理，需确认输入数据存在。上次会话未执行此步骤，本次为首次在新镜像上运行。

## [ ] Task 10: 汇总精度指标并生成报告
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 编写/运行报告生成脚本 `docker/runtime/generate_accuracy_report.py`：
    1. 读取 build/compile_success.txt 和 compile_failed.txt
    2. 遍历 build/accuracy_results/ 下所有 result.csv，解析余弦相似度、MSE、MAE
    3. 汇总为 Markdown 表格：模型名 | 前端 | 编译状态 | 精度状态 | 余弦相似度 | MSE | MAE | 备注
    4. 添加环境信息（wheel 版本、镜像标签、构建时间、Python/TVM 版本）
    5. 添加编译失败清单及原因分类
    6. 添加精度异常标注（如余弦相似度 < 0.99 的高亮）
  - 报告输出到 `build/xmnn-hub-caffe-onnx-sim-accuracy-report.md`
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: 报告文件生成在 build/ 目录
  - `programmatic` TR-10.2: 报告中模型总数 = 编译成功数 + 编译失败数 = 枚举总数
  - `programmatic` TR-10.3: 精度指标表格包含所有编译成功模型
  - `human-judgment` TR-10.4: 报告结构清晰，环境信息完整，失败原因可读，异常值有标注
- **Notes**: 报告中应明确标注哪些模型编译失败、哪些精度测试失败，便于后续针对性修复

## [ ] Task 11: 恢复 hub config.toml 原始配置并验证仓库清洁
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 从 `build/hub_config_backup/` 恢复 hub/caffe 和 hub/onnx 所有 config.toml
  - 可使用 `restore_configs.sh` 或手动 cp 备份文件回原位置
  - 在 `external/chaos/xmtools/` 目录执行 `git status`（在子模块内），确认无 config.toml 修改
  - `git diff` 应为空（针对 config.toml）
  - build/ 目录为新增产出物，不纳入版本控制（已在 .gitignore 中或应被忽略）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: 所有 config.toml 从备份恢复
  - `programmatic` TR-11.2: 在 xmtools 子模块内 `git status` 不显示 config.toml 为 modified
  - `programmatic` TR-11.3: `git diff -- models/hub/` 无输出
  - `programmatic` TR-11.4: 抽查几个之前被 patch 的 config.toml，确认 target 恢复为原始值（非 sim_vta2.0 的模型已复原）
- **Notes**: 这是最后一步，必须确保不污染 models/hub/ 子模块。恢复后再停止容器。

# Task Dependencies
```
Task 1 (环境预检)
  ├─→ Task 2 (wheel 构建)
  │     └─→ Task 3 (runtime 镜像构建)
  │           ├─→ Task 7 (枚举模型) ─┐
  │           └─→ Task 8 (批量编译) ─┤
  ├─→ Task 4 (扩展 patch 脚本) ─→ Task 6 (备份+patch) ─┘
  └─→ Task 5 (编排脚本) ──────────────────────────────┘
                                                         ↓
                                                    Task 9 (精度测试)
                                                         ↓
                                                    Task 10 (生成报告)
                                                         ↓
                                                    Task 11 (恢复+清洁)
```
- Task 4 和 Task 5 可与 Task 2/3 并行准备（脚本编写不依赖 wheel 构建完成）
- Task 7、Task 8 依赖 Task 3（镜像）、Task 5（编排脚本）、Task 6（config patch）
- Task 9 依赖 Task 8（必须先编译成功才能精度测试）
- Task 10 依赖 Task 9
- Task 11 依赖 Task 10（测试完成后才能恢复）
