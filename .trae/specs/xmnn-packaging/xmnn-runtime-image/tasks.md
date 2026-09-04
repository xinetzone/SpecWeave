# XMNN 客户运行时镜像 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 xmnn-runtime 目录结构与基础文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目录 `external/chaos/ai/xmnn-runtime/`
  - 创建子目录 `.agents/rules/`
  - 参考现有变体创建基础文件骨架：
    - `.env.example`（环境变量模板）
    - `.agents/rules/dockerfile.md`（本变体 Dockerfile 特有规则文档）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: ✅ 目录存在，包含 .env.example 和 .agents/rules/dockerfile.md
  - `human-judgement` TR-1.2: ✅ .env.example 变量名一致，支持 --cn 参数
- **Status**: 完成

## [x] Task 2: 编写 Dockerfile（三阶段构建）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 使用 `# syntax=docker/dockerfile:1.7-labs`
  - 三阶段构建（runtime-base 2个追加层 + whl-artifacts纯来源 + final 1个追加层 = 共3个追加层）：
    1. **runtime-base 阶段**（FROM devcontainer-base:conda-${BASE_TAG}）：
       - 重新声明 ARG、重置 SHELL、设置 LABEL
       - ENV PATH=/opt/conda/bin:${PATH} + OpenMP 环境变量
       - **追加层 1/3**：系统层——时区三层保证(tzdata+localtime+timezone文件)、libgomp1、计时器初始化
       - **追加层 2/3**：pip 层——根据 PIP_MIRROR 配置镜像源（aliyun/tuna/bfsu/official）
    2. **whl-artifacts 阶段**（FROM xmnn-whl-builder:latest）：纯来源阶段，无 RUN
       - ⚠️ 实现调整：whl路径从 `/builder/dist/` 改为 `/opt/xmnn-dist/`（需同步修改xmnn-whl-builder保留whl到该目录）
    3. **final 阶段**（FROM runtime-base）：
       - **追加层 3/3**：XMNN 运行时层——COPY whl + pip install（不带--no-deps）+ 内置6项验证 + build-info写入 + 清理
       - ENV TZ=Asia/Shanghai（第三层保证）
       - ENTRYPOINT [] + CMD打印版本信息
       - 12项 VALIDATION CHECKPOINT + BUILD TIMING SUMMARY
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-10, AC-11, AC-12
- **Test Requirements**:
  - `programmatic` TR-2.1: ✅ Dockerfile 语法正确（结构审查通过）
  - `programmatic` TR-2.2~TR-2.13: 待实际构建验证（Docker在当前沙箱不可用）
- **Status**: 完成（静态审查通过，实际构建待用户环境验证）

## [x] Task 3: 编写构建脚本 build.sh 和 build.bat
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - build.sh: 支持 --tag/--no-cache/--cn 参数，检查两个依赖镜像存在，自动运行验证
  - build.bat: Windows对等版本，chcp 65001 UTF-8支持
  - 构建上下文为 xmnn-runtime/ 目录
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1~TR-3.3: bash -n 语法检查通过，功能待实际环境验证
  - `programmatic` TR-3.4: ✅ 依赖镜像不存在时给出明确构建提示
- **Status**: 完成（bash语法检查通过）

## [x] Task 4: 编写运行时验证脚本 verify-runtime.sh
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 10项核心验证（Python版本/tvm/vta/xmnn/_libs/ctypes加载/tvm.build/时区/无构建工具/devuser权限）
  - PASS/FAIL计数，FAIL>0返回exit 1
  - ⚠️ 修复：去掉set -e，使用统一check函数捕获输出（避免单项测试失败导致脚本提前退出）
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.2: ✅ bash -n 语法检查通过
  - `programmatic` TR-4.1: 待构建后实际运行验证
- **Status**: 完成（语法检查通过）

## [x] Task 5: 编写 README.md 使用说明
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 9个章节：简介、前置依赖、快速开始、镜像特性、版本升级、验证、文件说明、构建参数
  - 包含Linux/Windows双版本构建和升级命令示例
- **Acceptance Criteria Addressed**: AC-9（升级路径文档）
- **Test Requirements**:
  - `human-judgement` TR-5.1: ✅ README清晰，包含构建/运行/升级三个核心流程
  - `human-judgement` TR-5.2: ✅ 升级命令具体可复制
- **Status**: 完成

## [x] Task 6: 端到端测试与镜像验证
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 静态验证：文件完整性检查、bash -n语法检查（build.sh/verify-runtime.sh均通过）
  - Dockerfile结构审查：三阶段、12项检查点、ENTRYPOINT空、时区三层保证均正确
  - 实际docker build因沙箱环境无Docker而未执行，需用户在本地环境运行 ./build.sh 验证
- **Acceptance Criteria Addressed**: AC-2~AC-10（静态层面覆盖）
- **Test Requirements**:
  - `programmatic` TR-6.1~TR-6.5: 静态验证通过，实际构建待用户环境执行
- **Status**: 静态验证完成，实际构建待用户验证

## [x] Task 7: 更新 chaos/ai 主目录构建入口（可选）
- **Priority**: low
- **Depends On**: Task 6
- **Description**: 
  - 评估结果：xmnn-runtime是独立客户发布镜像（xmnn-runtime:tag），不属于devcontainer-base变体链，有独立构建脚本，无需集成主入口
- **Acceptance Criteria Addressed**: 无（非必需）
- **Status**: 跳过（不需要）

## 额外修复（非计划任务但必要）
- **修复 xmnn-whl-builder/Dockerfile**: FINAL阶段增加 `/opt/xmnn-dist/` 目录保留whl文件，供下游runtime镜像COPY使用（原设计中whl安装后被删除，导致runtime无法获取）

## 任务依赖关系图
```
Task 1 (目录结构) ✅
  └─> Task 0 (修复whl-builder保留whl) ✅
  └─> Task 2 (Dockerfile) ✅
       ├─> Task 3 (构建脚本) ✅
       ├─> Task 4 (验证脚本) ✅
       └─> Task 6 (端到端测试 - 静态通过) ✅
  └─> Task 5 (README) ✅
  └─> Task 7 (统一入口 - 跳过) ✅
```
