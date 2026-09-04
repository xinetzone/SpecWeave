# devcontainer-base 变体 Dockerfile 重构优化 - Product Requirement Document

> **Spec状态**：v2.1（阶段一完成！10模块共享框架全部就绪，等待阶段二向后兼容+模板更新）
> **更新日期**：2026-08-15
> **方法论链路**：I(洞察)→F(第一性原理)→V(对抗审查)→A(原子化)

## Overview
- **Summary**: 提取 devcontainer-base variants/ 目录下所有变体 Dockerfile 中的重复构建框架代码到 `variants/shared/lib/` 共享脚本库。变体 Dockerfile 只保留变体差异逻辑（安装什么包、验证什么功能），简化维护成本。
- **Purpose**: 解决当前每个变体独立实现完整构建框架导致的代码重复、维护成本高、bug修复不同步等问题。
- **Current Status**: ✅ **阶段一完成** - 10个模块的共享构建框架全部实现并通过语法检查。logging.sh/timer.sh为已有高质量模块，其余8个模块（mirror/install-helpers/ft-guards/cleanup/build-info/verify/permissions/variant-framework）已按Spec实现。下一步：阶段二向后兼容、框架集成验证、模板更新。
- **Target Users**: 维护 devcontainer-base 镜像的开发者、新增变体的开发者、CI/CD 系统。

## Goals
- ✅ 保留现有 `logging.sh`（双格式text+JSON日志）和 `timer.sh`（/root/.variant-timers/安全存储）的优秀设计
- 在 `variants/shared/lib/` 下补全剩余8个模块化脚本，形成完整构建框架
- 框架总计10个模块：logging/timer/mirror/install-helpers/ft-guards/cleanup/build-info/verify/permissions + 入口脚本
- 增强镜像源配置支持 official/tuna/aliyun/bfsu 四种conda镜像 + 性能参数（线程/solver/超时/重试）
- 更新 `_template/Dockerfile` 为使用新框架的极简模板（代码量<100行，减少70%+）
- 增量迁移现有 **5** 个变体到新框架（按依赖顺序：conda-llvm → onnx-dev → onnx-pytorch/onnx-quantized → ai-dev）
- 保持100%向后兼容：迁移过程中变体仍可正常构建，功能无任何回归
- 所有现有变体的功能、验证检查、构建输出格式保持不变

## Non-Goals (Out of Scope)
- 不重构 devcontainer-base 根目录的主 Dockerfile（主Dockerfile是7阶段基础镜像构建，与变体追加层模式不同）
- 不重写已完成的 `logging.sh` 和 `timer.sh`（保留现有高质量设计）
- 不修改 variants/ 以外的构建脚本（如根目录 scripts/build.sh）
- 不改变镜像层级结构或构建缓存策略
- 不新增或删除任何变体，只重构现有变体（conda变体已下线，当前5个变体）
- 不修改镜像内的软件版本或配置
- 不重构 entrypoint.sh、healthcheck.sh 等运行时脚本

## Background & Context
- **当前变体列表（5个）**：conda-llvm、onnx-dev、onnx-pytorch、onnx-quantized、ai-dev（原Spec说7个含conda，实际conda已下线）
- **已有框架模块**：
  - `shared/lib/logging.sh`（237行）：text+JSON双格式日志，支持log_metric/log_event/log_summary，含variant_*专用函数
  - `shared/lib/timer.sh`（204行）：构建阶段计时，计时器存`/root/.variant-timers/`（隐藏目录，不会被rm -rf /tmp/*删除），输出BUILD TIMING SUMMARY表格
- **重复代码问题**：每个变体Dockerfile仍有约300-600行重复的构建框架代码：
  - 计时器初始化/阶段计时/汇总表：~50行/变体（且仍用旧的/tmp/路径有被清理风险）
  - conda镜像源case配置（含性能参数）：~80行/变体
  - `conda_install_group` 辅助函数：~30行/变体
  - free-threading完整性守卫：~20行/变体
  - 清理逻辑：~20行/变体
  - build-info元数据写入：~40行/变体
  - 基础服务验证：~30行/变体
  - 权限设置：~20行/变体
- **典型问题**：计时器文件被清理bug已在新timer.sh修复，但所有变体仍使用旧方式；conda_install_group函数在每个变体中重复定义，bug修复需要同步5个文件
- **共享脚本现状**：`shared/scripts/conda-mirror-setup.sh`仅支持2种conda镜像，缺性能参数配置
- **新增变体成本**：复制粘贴200+行模板代码，容易遗漏关键检查或引入错误

## Functional Requirements

### FR-1 ~ FR-2: 已有模块（保留，不重写）
- **FR-1**: `shared/lib/logging.sh` 已实现，包含：通用日志API（log_debug/info/ok/warn/error/fatal）、variant专用函数（variant_stage_header/variant_section_header/variant_log_build/ok/info/warn/error/timer/check）、JSON Lines输出支持、metric/event/summary API
- **FR-2**: `shared/lib/timer.sh` 已实现，包含：variant_timer_start/variant_timer_stage/variant_timer_summary函数，计时器存储在`/root/.variant-timers/`（修复rm -rf /tmp/*删除bug），自动输出BUILD TIMING SUMMARY表格

### FR-3 ~ FR-9: 待实现模块
- **FR-3**: 实现镜像源模块 `mirror.sh`，提供 `variant_configure_mirrors` 函数
  - 支持 CONDA_MIRROR: official/tuna/aliyun/bfsu 四种源
  - 支持 PIP_MIRROR: official/tuna/aliyun 三种源
  - 支持 APT_MIRROR: official/tuna/aliyun 三种源
  - 自动配置conda性能参数：线程数(8)、超时(30/300s)、重试(5)、backoff(3)、libmamba solver
  - 自动配置root和devuser的pip.conf
- **FR-4**: 实现安装辅助模块 `install-helpers.sh`，提供：
  - `conda_install_group <group_name> <description> <packages...>`：结构化日志、计时、失败诊断、set +e/-e错误处理
  - `pip_install_group <group_name> <description> <packages...>`：同上，支持pip安装
- **FR-5**: 实现free-threading守卫模块 `ft-guards.sh`，提供：
  - `assert_free_threading`：检查sys._is_gil_enabled() == False
  - `assert_python_cp314t`：检查python build string包含cp314t
  - `assert_package_present <pkg_name>`：正向守卫，检查包可导入
  - `assert_package_absent <pkg_name>`：负向守卫，检查包不可导入
- **FR-6**: 实现清理模块 `cleanup.sh`，提供：
  - `cleanup_pycache`：删除__pycache__和.pyc/.pyo
  - `cleanup_conda_pip_cache`：conda clean -yafq + pip cache purge
  - `cleanup_apt`：apt-get clean + 删除/var/lib/apt/lists/*
  - `cleanup_tmp`：安全清理/tmp/* /var/tmp/*（保留/root/.variant-timers/）
  - `cleanup_all`：一键执行所有清理
  - `cleanup_binaries`（可选）：strip二进制、删除静态库
- **FR-7**: 实现build-info模块 `build-info.sh`，提供：
  - `variant_write_build_info <variant_name> <base_image> [extra_kv_pairs...]`
  - 自动写入通用字段：BUILD_DATE/VARIANT/BASE_IMAGE/CONDA_MIRROR/PIP_MIRROR/APT_MIRROR/SERVICES_PRESERVED/BUILD_TIMER
  - 支持变体自定义额外key=value字段
  - 写入路径：`/etc/devcontainer-variant-<variant_name>-build-info`
  - 写入后自动cat输出到日志
- **FR-8**: 实现基础验证模块 `verify.sh`，提供：
  - `verify_base_services`：验证docker、supervisord、sshd可用
  - `verify_conda_main_env`：验证conda main环境存在、python可执行
  - `verify_devuser_access`：验证devuser存在、可访问conda、可执行python
  - `verify_bash_syntax <script_path>`：bash -n语法检查
  - `verify_validation_header`：输出[VALIDATION CHECKPOINT]标准横幅
- **FR-9**: 实现权限模块 `permissions.sh`，提供：
  - `ensure_conda_permissions`：chown -R root:root /opt/conda + chmod -R a+rX
  - `ensure_executable_permissions <path>`：确保路径下二进制可执行
  - `ensure_devuser_bashrc`：确保devuser .bashrc所有权正确

### FR-10: 框架入口
- **FR-10**: 实现框架入口脚本 `variant-framework.sh`
  - 按正确顺序source所有模块：logging → timer → mirror → install-helpers → ft-guards → cleanup → build-info → verify → permissions
  - 支持 `VARIANT_DEBUG=1` 环境变量启用set -x调试输出
  - 提供 `variant_framework_version` 变量标识框架版本
  - source后所有函数可用，无报错
  - 不修改shell选项（set -euo pipefail保持调用者设置）

### FR-11 ~ FR-12: 向后兼容和模板
- **FR-11**: 更新 `shared/scripts/conda-mirror-setup.sh` 保持向后兼容，内部调用 `mirror.sh` 函数
- **FR-12**: 更新 `_template/Dockerfile` 使用新框架实现极简模板
  - 模板开头 COPY shared/lib/ 所有脚本到镜像内
  - 每个RUN heredoc开头 source variant-framework.sh
  - 使用框架函数替代内联代码
  - 清晰标注 `__VARIANT_INSTALL__`、`__VARIANT_CONFIG__`、`__VARIANT_VALIDATE__` 三个占位符
  - 模板代码量 < 100行（原模板277行，减少~64%+）

### FR-13 ~ FR-17: 变体迁移
- **FR-13**: 试点迁移 conda-llvm 变体到新框架
- **FR-14**: 迁移 onnx-dev 变体到新框架
- **FR-15**: 迁移 onnx-pytorch 变体到新框架
- **FR-16**: 迁移 onnx-quantized 变体到新框架
- **FR-17**: 迁移 ai-dev 变体到新框架

### FR-18 ~ FR-20: 验证目标
- **FR-18**: 迁移后每个变体Dockerfile代码量减少 70% 以上（平均从~400行减少到~120行以内）
- **FR-19**: 所有迁移后变体构建日志的计时器汇总表格式、[TIMER]标记、build-info格式与迁移前完全一致
- **FR-20**: 所有测试脚本(test-*.sh)全部通过，无功能回归

## Non-Functional Requirements
- **NFR-1**: 构建性能：使用共享脚本后构建速度不降低（脚本source开销可忽略，单独COPY层利于缓存）
- **NFR-2**: 构建缓存：共享脚本放在单独的COPY层，不影响前面层的缓存；脚本修改时只需要重建变体的追加层
- **NFR-3**: 可维护性：新增变体只需要在模板基础上修改 30-80 行差异代码
- **NFR-4**: 一致性：所有变体使用相同的日志格式、计时器格式、错误处理方式
- **NFR-5**: 可调试性：框架脚本支持 `VARIANT_DEBUG=1` 环境变量启用set -x调试输出；错误信息带函数名
- **NFR-6**: 向后兼容性：迁移过程中旧变体Dockerfile仍可正常构建，新旧可以共存；conda-mirror-setup.sh独立可执行脚本保留
- **NFR-7**: 错误信息清晰：框架函数输出明确的错误位置和原因，便于调试
- **NFR-8**: 零外部依赖：所有脚本只用bash内置命令和基础工具(awk/grep/sed/find等)，基础镜像已包含，不引入新依赖

## Constraints
- **Technical**: 
  - 必须使用bash脚本（与现有Dockerfile RUN heredoc兼容）
  - 脚本必须支持 `set -euo pipefail` 严格模式
  - 框架必须在每个RUN heredoc开头source（因为Docker每个RUN是独立shell进程）
  - 共享脚本放在 `variants/shared/lib/` 目录
  - 所有函数必须有清晰的命名前缀：variant_/verify_/cleanup_等
  - 不引入任何新的系统依赖
  - 保留现有logging.sh和timer.sh，不重写、不降级API
  - 计时器存储路径保持 `/root/.variant-timers/`（与现有timer.sh一致）
- **Business**: 无特殊业务约束
- **Dependencies**:
  - 依赖Docker BuildKit支持（项目已强制要求）
  - 依赖现有logging.sh和timer.sh作为基础

## Assumptions
- Docker BuildKit已启用（项目现有Dockerfile已使用`# syntax=docker/dockerfile:1.7-labs`）
- 现有变体的功能和验证逻辑是正确的，重构只做代码提取和简化，不改变逻辑
- 共享脚本在FROM devcontainer-base:*之后的层执行，基础镜像内已有bash和基础工具
- 增量迁移期间可以同时存在使用旧框架和新框架的变体
- 每个RUN阶段是独立进程，需要在每个heredoc开头source框架

## Acceptance Criteria

### AC-1: 框架模块完整性
- **Given**: variants/shared/lib/目录
- **When**: 列出文件
- **Then**: 目录包含 logging.sh、timer.sh、mirror.sh、install-helpers.sh、ft-guards.sh、cleanup.sh、build-info.sh、verify.sh、permissions.sh、variant-framework.sh 共10个脚本
- **Verification**: programmatic（文件存在性检查）

### AC-2: 所有框架脚本语法正确
- **Given**: variants/shared/lib/*.sh
- **When**: 对每个脚本执行 `bash -n script.sh`
- **Then**: 所有脚本无语法错误
- **Verification**: programmatic（bash -n检查）

### AC-3: 框架入口可正常source
- **Given**: variant-framework.sh
- **When**: bash -c "source variants/shared/lib/variant-framework.sh && declare -F"
- **Then**: 无错误输出，所有框架函数已定义
- **Verification**: programmatic（source测试+函数列表检查）

### AC-4: mirror.sh支持四种conda镜像
- **Given**: mirror.sh中variant_configure_mirrors函数
- **When**: 分别用CONDA_MIRROR=official/tuna/aliyun/bfsu调用
- **Then**: 生成对应的.condarc配置，pip.conf配置正确，性能参数已设置
- **Verification**: programmatic（配置内容检查）

### AC-5: conda-mirror-setup.sh向后兼容
- **Given**: 更新后的shared/scripts/conda-mirror-setup.sh
- **When**: 直接执行脚本配置镜像
- **Then**: 功能正常，与之前行为一致，内部调用mirror.sh函数
- **Verification**: programmatic（脚本可执行+配置检查）

### AC-6: _template/Dockerfile更新为极简模板
- **Given**: 更新后的_template/Dockerfile
- **When**: 查看文件内容
- **Then**: 模板使用variant-framework.sh，代码量<100行，3个核心占位符清晰标注
- **Verification**: human-judgment + programmatic（行数统计+语法检查）

### AC-7: conda-llvm试点变体迁移成功
- **Given**: 迁移后的conda-llvm/Dockerfile
- **When**: 执行docker build并运行所有验证
- **Then**: 镜像构建成功，LLVM/clang/cmake/ninja可用，Hello World编译测试通过，free-threading验证通过，所有原有检查通过，镜像大小无显著增加(<3%)
- **Verification**: programmatic（docker build + 所有验证项+测试脚本）

### AC-8 ~ AC-11: 其他变体迁移成功
- AC-8: onnx-dev迁移成功，纯ONNX冒烟测试通过，torch缺席检查通过
- AC-9: onnx-pytorch迁移成功，PyTorch CPU可用，ONNX导出验证通过
- AC-10: onnx-quantized迁移成功，量化工具可用，动态/静态量化测试通过
- AC-11: ai-dev迁移成功，transformers/datasets等50+包可用，Jupyter双kernel正确
- **Verification**: programmatic（每个变体docker build + 对应test-*.sh脚本）

### AC-12: 代码量减少达标
- **Given**: 所有变体迁移完成
- **When**: 统计迁移前后变体Dockerfile总行数
- **Then**: 平均代码量减少70%以上
- **Verification**: programmatic（行数统计对比）

### AC-13: 无功能回归
- **Given**: 所有变体镜像构建完成
- **When**: 运行每个变体的所有验证检查项和test-*.sh测试脚本
- **Then**: 所有检查项和测试全部通过，与迁移前行为一致
- **Verification**: programmatic（全量测试）

### AC-14: 构建输出格式一致
- **Given**: 迁移后的变体构建日志
- **When**: 查看构建日志输出
- **Then**: BUILD TIMING SUMMARY表格格式、[TIMER]标记格式、[OK]/[ERROR]日志格式、build-info文件格式与迁移前完全一致
- **Verification**: human-judgment + programmatic（日志关键字检查）

## Open Questions (已通过V阶段对抗审查解决)
- [x] 主Dockerfile的重复辅助函数是否也提取？→ 不提取，主Dockerfile模式不同，保持独立
- [x] 是否需要为共享框架脚本编写单元测试？→ bash -n语法检查 + source函数存在检查 + 试点变体构建验证
- [x] 迁移完成后是否删除旧的内联代码？→ 是的，每个变体迁移后删除冗余内联代码
- [x] 计时器用/var/tmp/还是/root/.variant-timers/？→ 用/root/.variant-timers/，与现有timer.sh一致，更安全
- [x] 每个RUN阶段需要重新source框架吗？→ 是的，因为Docker每个RUN是独立shell进程，这是设计要求
- [x] conda-mirror-setup.sh保留吗？→ 保留作为独立可执行脚本，内部调用mirror.sh，保持向后兼容
