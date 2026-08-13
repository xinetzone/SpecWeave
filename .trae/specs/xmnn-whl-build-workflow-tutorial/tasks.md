# Tasks

## 前置：资料采集与事实整理（R 阶段）
- [x] Task 1: 采集 xmtools 构建打包源码关键事实
  - [x] 1.1 阅读 xmtools/README.md、AGENTS.md 提炼项目定位、工具链、目录结构、产出物
  - [x] 1.2 阅读 Dockerfile 提炼构建环境（ubuntu 26.04 + Miniconda + LLVM22 + 国内镜像 + 环境变量）
  - [x] 1.3 阅读 build-and-test.sh / run-build.sh / verify-wheel.sh 提炼 Docker 一键构建三阶段流程
  - [x] 1.4 阅读 tasks.py 提炼本地 invoke 构建任务链
  - [x] 1.5 阅读 pyproject.toml / CMakeLists.txt 提炼打包配置与 CMake 安装规则
  - [x] 1.6 阅读 _xmnn_bootstrap.py / xmnn_bootstrap.pth 提炼 AST 兼容层与 bootstrap 机制
  - [x] 1.7 通过 G1 质量门：事实无因果推断词，可追溯（编号 F-001 起）

## 洞察与结构设计（I 阶段）
- [x] Task 2: 提炼核心洞察并确定文档结构
  - [x] 2.1 提炼 3 条核心洞察（陈述/证据/反常识/行动四元组），通过 G2 质量门
  - [x] 2.2 确定文档章节结构（Docker 路径 / invoke 路径 / 验证 / CMake / bootstrap / FAQ），输出路径 `external/chaos/ai/.agents/docs/xmnn-whl-build-workflow.md`
  - [x] 2.3 确认 frontmatter 格式与 chaos/ai 既有规范文档一致（参考 rules/build.md、verify.md）

## 教程生成（E 阶段，实施）
- [x] Task 3: 生成教程文档
  - [x] 3.1 编写 frontmatter 与总览章节（项目定位、工具链、目录结构、产出物、环境要求）
  - [x] 3.2 编写 Docker 一键构建路径章节（Dockerfile 环境 + build-and-test.sh 三阶段 + 三种模式）
  - [x] 3.3 编写容器内构建 run-build.sh 章节（环境检查、pyproject 补丁、Nuitka 编译 vta/xmnn、python -m build）
  - [x] 3.4 编写本地 invoke 构建路径章节（tasks.py 任务链详解）
  - [x] 3.5 编写 wheel 验证标准章节（verify-wheel.sh 9 项测试 + auditwheel + 依赖解析）
  - [x] 3.6 编写 CMake 打包原理章节（_libs 打包、RPATH、数据目录、chmod）
  - [x] 3.7 编写 AST 兼容层与 bootstrap 机制章节
  - [x] 3.8 编写常见问题排查表章节
  - [x] 3.9 检查单文件 <400 行、交叉引用相对路径、无断链

## 验证与交付（V/C 阶段）
- [x] Task 4: 对抗审查（V）与质量门
  - [x] 4.1 对教程进行多视角对抗审查（V 门：5 条具体意见，全部采纳修正）
    - 意见1：tasks.py "typer+dataclass 风格"为虚构 → 改为 "invoke @task 装饰器风格"（源码仅 `from invoke import task`）
    - 意见2：docker run 示例与脚本实际行为脱节 → 改为真实挂载 `/tmp/run-build.sh:ro` 并执行 `/tmp/run-build.sh`
    - 意见3：运行时依赖 21 vs 19 矛盾 → 核对 pyproject.toml 实为 19 个，统一为 19
    - 意见4：wheel 157MB 却含 186.4MB libLLVM 矛盾 → 标注"压缩后大小"+ "压缩率需实测确认"
    - 意见5：LLVM 版本"四包一致"表述错误 → 改为"六个 LLVM 族包（llvm/llvmdev/clang/clangxx/lld/llvm-tools）均锁 =22.1"
  - [x] 4.2 逐项核对 spec.md 的 AC-1~AC-10 验收标准（全部通过）
  - [x] 4.3 验证 frontmatter 合规、交叉链接有效（AC-10 全指向存在文件）、内容与 xmtools 源码一致

# Task Dependencies
- [Task 1] 无依赖（资料采集）
- [Task 2] 依赖 [Task 1]（需事实清单）
- [Task 3] 依赖 [Task 2]（需章节结构）
- [Task 4] 依赖 [Task 3]（需完整教程）
