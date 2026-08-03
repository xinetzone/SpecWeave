# Tasks

## 阶段 1：全面复盘（七概念方法论 R→I→E→V→A→C）

- [ ] Task 1: 复盘前置环境确认
  - [ ] 1.1 确认 `dist/` 已有 wheel 文件名与版本（`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`，约185MB）
  - [ ] 1.2 确认 WSL 内 Docker 可用（`docker info` 通过），确认 `npu_tvm`/`npuusertools` 兄弟目录存在
  - [ ] 1.3 恢复/确认 `npu_tvm`、`npuusertools` 的 git 状态（submodule 未污染）

- [ ] Task 2: R 阶段 - 事实采集（代码结构审查 + 功能模块评估）
  - [ ] 2.1 审查 `pyproject.toml`（build-system、dependencies、optional-dependencies、scikit-build 配置）
  - [ ] 2.2 审查 `CMakeLists.txt`（Nuitka .so 安装、_libs 打包、数据目录、RPATH、可执行权限）
  - [ ] 2.3 审查 `tasks.py`（invoke 任务链、Nuitka 编译、PREAMBLE 注入机制）
  - [ ] 2.4 审查 `docker/**`（dev-llvm22 / runtime / serve / 根 Dockerfile / docker-compose）
  - [ ] 2.5 审查 `scripts/verify_wheel.py` 与 `scripts/check_env.sh`
  - [ ] 2.6 审查 `sdk/**`（tools 6 个 CLI、models、测试脚本）
  - [ ] 2.7 审查 `.agents/**` 项目规则与项目约束一致性
  - [ ] 2.8 输出事实清单（F-001 起，无因果词，≥20 条）

- [ ] Task 3: I 阶段 - 洞察（潜在问题识别 + 性能优化建议）
  - [ ] 3.1 基于事实清单做 5-Whys 根因分析
  - [ ] 3.2 提炼 ≥3 条洞察（四元组：陈述/证据/反常识/行动），引用 F-xxx 编号
  - [ ] 3.3 输出 P0/P1/P2 潜在问题清单（含根因与修复建议）
  - [ ] 3.4 输出性能优化建议（镜像体积、wheel 体积、构建耗时、运行时加载）

- [ ] Task 4: E 阶段 - 模式萃取 + V 阶段 - 对抗审查
  - [ ] 4.1 萃取 ≥2 个可迁移方法论模式（含触发/步骤/反模式/检验/迁移）
  - [ ] 4.2 V 对抗审查：4 视角（魔鬼代言人/新人/老板/未来）审查洞察与模式，≥5 条意见，采纳 ≥2 条修正

- [ ] Task 5: 复盘报告归档（三件套）
  - [ ] 5.1 生成 `README.md`（主报告：事实+洞察+问题+优化）
  - [ ] 5.2 生成 `insight-extraction.md`（模式萃取）
  - [ ] 5.3 生成 `actionable-items.md`（行动项，含优先级/Owner/验收标准）
  - [ ] 5.4 归档至 `.agents/docs/retrospective/reports/task-reports/retrospective-xmtools-20260803/`
  - [ ] 5.5 更新 `.agents/docs/retrospective/reports/task-reports/README.md` 索引

## 阶段 2：基于复盘修复构建缺陷

- [ ] Task 6: 修复构建/打包缺陷
  - [ ] 6.1 按复盘 P0/P1 问题修复 `pyproject.toml` / `CMakeLists.txt` / `tasks.py` / `docker/**` / `scripts/verify_wheel.py`
  - [ ] 6.2 确保修复不破坏既有构建链路（语法检查、配置校验）

## 阶段 3：打包标准 whl + 验证

- [ ] Task 7: 打包 whl
  - [ ] 7.1 在 WSL Docker 内执行 `python -m build --wheel --no-isolation`（或 `inv build-all`）
  - [ ] 7.2 确认生成 `dist/xmnn-<version>-cp314-cp314-linux_x86_64.whl`
  - [ ] 7.3 确认 wheel 内容完整（_libs、Nuitka .so、bootstrap、数据目录、relay/std、vta_hw/config）

- [ ] Task 8: 11 项验证
  - [ ] 8.1 执行 `scripts/verify_wheel.py` 或 `inv verify`
  - [ ] 8.2 全部验证项通过（import tvm/vta/xmnn、_libs、libtvm.so、tvm.build、relay/std、vta_hw/config、bootstrap.pth、数据目录、依赖完整性）

## 阶段 4：构建并导出生产级 Docker 镜像

- [ ] Task 9: 构建生产级镜像
  - [ ] 9.1 构建/重建 runtime 镜像（ubuntu:26.04 + Miniconda + Python 3.14 + xmnn wheel，空 ENTRYPOINT，时区 Asia/Shanghai）
  - [ ] 9.2 镜像内冒烟测试（import tvm/vta/xmnn + tvm.build）
  - [ ] 9.3 体积优化检查（清理缓存、裁剪无用依赖）

- [x] Task 10: 导出镜像
  - [x] 10.1 `docker save` 导出为 `dist/xmnn-production-*.tar`（`dist/xmnn-production-1.2.1-alpha.tar`，1.35GB）
  - [x] 10.2 `docker load` 还原验证，确认可正常运行（Python 3.14.6 / CST 时区 / tvm 0.19.0 / xmnn import OK）

## 阶段 5：收尾（C 原子提交）

- [x] Task 11: 复盘闭环与原子提交
  - [x] 11.1 更新 BUILD_REPORT.md / 相关文档（全量构建报告已含依赖审计与修复记录）
  - [x] 11.2 对修复变更执行原子提交（Conventional Commits，中文描述，commit `cef2dc3`）
  - [x] 11.3 汇总质量门通过记录与产出物清单

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 6]
- [Task 8] depends on [Task 7]
- [Task 9] depends on [Task 8]
- [Task 10] depends on [Task 9]
- [Task 11] depends on [Task 10]

# 并行化说明

- Task 1（环境确认）与具体代码审查（2.1-2.7）可部分并行
- 阶段 2 修复与阶段 3 打包存在依赖（先修复再打包），需顺序执行
- 阶段 4 镜像构建依赖阶段 3 的 wheel 产物，需顺序执行