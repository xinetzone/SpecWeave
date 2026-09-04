# xmnn-whl-builder 干净重编译模式 - The Implementation Plan

## [x] Task 1: 修改 build-wheel.sh 支持 CLEAN_REBUILD 环境变量
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 build-wheel.sh 的 ccache 初始化段（约 L71-83），添加对 `CLEAN_REBUILD` 环境变量的检测
  - 当 `CLEAN_REBUILD=1` 时：
    - 设置 `export CCACHE_DISABLE=1`（ccache 官方禁用开关，不查不写，透明透传）
    - 执行 `ccache -z` 清零统计计数器（便于日志确认零命中）
    - 打印醒目的干净模式横幅日志（带颜色，与 log_banner 风格一致）
  - 当 `CLEAN_REBUILD!=1` 时：保持原有 ccache 启用逻辑不变
  - 在 Environment Check 段添加 ccache 状态输出（启用/禁用 + 当前统计）
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: 设置 CLEAN_REBUILD=1 时，日志出现 "CLEAN REBUILD" 标识且 ccache 被标记为 disabled
  - `programmatic` TR-1.2: 不设置 CLEAN_REBUILD 时，ccache 正常启用，与当前行为一致
  - `human-judgment` TR-1.3: 代码风格与现有脚本一致，使用共享日志函数（log_banner/log_warn/log_ok）
- **Notes**: ccache -z 只清零统计计数器，不清空缓存目录，确保不破坏已有缓存

## [x] Task 2: 修改 Dockerfile 添加 CLEAN_REBUILD ARG/ENV
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 Dockerfile builder 阶段的现有 ARG/ENV 块（约 L46-53，NUITKA_JOBS/NUITKA_PLUGINS 等）之后，添加：
    - `ARG CLEAN_REBUILD=0`
    - `ENV CLEAN_REBUILD=${CLEAN_REBUILD}`
  - 位置应在 RUN 调用 build-wheel.sh（L69-72）之前，确保 ENV 在执行编译脚本时生效
  - 在注释中说明该参数用途（配合 --clean-rebuild 宿主选项，禁用 ccache 确保全量重编译）
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: Dockerfile 首行仍为 # syntax=docker/dockerfile:1.7-labs
  - `programmatic` TR-2.2: CLEAN_REBUILD ARG 默认值为 0，ENV 正确传递
  - `human-judgment` TR-2.3: 注释清晰，与现有注释风格一致
- **Notes**: ARG 默认值为 0 确保不指定时不改变行为

## [x] Task 3: 修改 build.sh 添加 --clean-rebuild/-C 选项
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 build.sh 顶部变量声明区（约 L33-43）添加 `CLEAN_REBUILD=0`
  - 在 usage() 函数（约 L74-112）中添加选项文档：
    - `--clean-rebuild, -C  干净重编译：禁用 ccache + 绕过 Docker 层缓存，确保 tvm/vta/xmnn 全量重新编译`
  - 在参数解析 while 循环（约 L114-152）中添加 `-C|--clean-rebuild)` 分支：设置 `CLEAN_REBUILD=1`、`NO_CACHE=1`
  - 在 BUILD_ARGS 构建段（约 L159-167），当 CLEAN_REBUILD=1 时追加 `--build-arg CLEAN_REBUILD=1` 到 BUILD_ARGS
  - 在构建配置 log_kv 输出段（约 L256-265）添加干净模式状态显示
  - 在源码快照/NO_CACHE 处理段（约 L447-468），当 CLEAN_REBUILD=1 时打印明确日志说明同时禁用了 ccache 和层缓存
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: `./build.sh -h` 输出包含 --clean-rebuild/-C 说明
  - `programmatic` TR-3.2: 指定 -C 时 NO_CACHE 自动设为 1，BUILD_ARGS 同时包含 --no-cache 和 --build-arg CLEAN_REBUILD=1
  - `programmatic` TR-3.3: 不指定 -C 时 BUILD_ARGS 不含 CLEAN_REBUILD（使用 Dockerfile 默认值 0）
  - `programmatic` TR-3.4: 配置日志显示干净重编译模式状态
  - `human-judgment` TR-3.5: 参数解析风格与现有选项一致（--cn/-v/-F 等）
- **Notes**: -C 隐含 -F/--no-cache，用户不需要同时指定两个

## [x] Task 4: 更新 .agents/rules/dockerfile.md 规范文档
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 在 .agents/rules/dockerfile.md 的"构建参数"表格（约 L131-134）中添加 CLEAN_REBUILD 参数行：
    - 参数名: CLEAN_REBUILD
    - 默认值: 0
    - 说明: 干净重编译开关，设为 1 时通过 CCACHE_DISABLE=1 禁用 ccache，同时建议配合 --no-cache 使用；由 build.sh --clean-rebuild/-C 自动传递
  - 在核心约束中适当位置补充 ccache 禁用机制说明（在 §4 ccache 编译缓存节末尾添加"干净重编译"子节）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgment` TR-4.1: 文档更新准确反映代码变更，与现有文档风格一致
  - `programmatic` TR-4.2: Markdown 格式正确，无断链
- **Notes**: 文档更新跟随代码变更，保持规范与实现同步

## [ ] Task 5: 端到端验证 - 默认构建行为不变
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在 WSL 环境下执行 `cd external/chaos/ai/xmnn-whl-builder && bash build.sh --cn`
  - 确认构建成功，verify-wheel.sh 11/11 PASS
  - 确认构建日志中 ccache 正常启用（不出现 CLEAN REBUILD 横幅）
  - 确认 /opt/xmnn-dist/ 中 wheel 文件存在
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 构建退出码为 0
  - `programmatic` TR-5.2: verify-wheel.sh 输出 11 项全部 PASS（无 FAIL/ERROR）
  - `programmatic` TR-5.3: docker run 验证 import tvm/vta/xmnn 成功
- **Notes**: 此为回归验证，确保默认路径未被破坏

## [ ] Task 6: 端到端验证 - 干净重编译模式
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 执行 `bash build.sh --clean-rebuild --cn -v`
  - 检查构建日志中：
    - 出现 "干净重编译模式: 是" 配置日志
    - docker build 命令包含 --build-arg CLEAN_REBUILD=1 和 --no-cache
    - 容器内 build-wheel.sh 输出 CLEAN REBUILD 横幅
    - ccache 状态显示为 disabled
  - 确认构建成功，verify-wheel.sh 11/11 PASS
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 构建退出码为 0
  - `programmatic` TR-6.2: 日志包含 CLEAN REBUILD 标识且 ccache disabled
  - `programmatic` TR-6.3: docker build 命令行包含 --no-cache 和 --build-arg CLEAN_REBUILD=1
  - `programmatic` TR-6.4: verify-wheel.sh 11/11 PASS
  - `programmatic` TR-6.5: 镜像内 import tvm/vta/xmnn 正常
- **Notes**: 核心验证任务，确认干净模式确实生效

## [ ] Task 7: 验证 - 干净模式不破坏 ccache 缓存
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 完成 Task 5（普通构建，填充 ccache）和 Task 6（干净构建）后，再执行一次普通构建 `bash build.sh --cn`
  - 观察第二次普通构建（Task 5 为第一次普通）的 ccache 命中率
  - 确认 ccache 仍然可用（未被干净模式清空/破坏）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 第三次构建（普通）ccache 有缓存命中（或编译时间明显短于全量编译）
  - `programmatic` TR-7.2: ccache 统计中 cache hit rate > 0（若非首次构建）
- **Notes**: 此为缓存隔离验证，证明 CCACHE_DISABLE=1 是旁路而非清空
