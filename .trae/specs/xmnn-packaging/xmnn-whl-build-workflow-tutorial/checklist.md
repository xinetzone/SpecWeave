# Checklist

## 资料采集（R 阶段）
- [x] 已从 xmtools 源码采集充分事实，通过 G1 质量门（无因果词、可追溯）
- [x] Dockerfile / build-and-test.sh / run-build.sh / verify-wheel.sh / tasks.py / pyproject.toml / CMakeLists.txt / bootstrap 均已研读

## 洞察与结构（I 阶段）
- [x] 提炼 ≥3 条核心洞察，通过 G2 质量门（四元组完整）
- [x] 文档章节结构确定，覆盖 Docker / invoke / 验证 / CMake / bootstrap / FAQ

## 教程生成（E 阶段）
- [x] [AC-1] 文档置于 chaos/ai/.agents/docs/xmnn-whl-build-workflow.md，命名 kebab-case
- [x] [AC-2] frontmatter 含 id/title/source/date/tags，YAML 格式
- [x] [AC-3] Docker 一键构建路径覆盖完整（Dockerfile 环境 + 三阶段 + 三模式）
- [x] [AC-4] 容器内构建 run-build.sh 覆盖完整（环境检查/补丁/Nuitka/build）
- [x] [AC-5] 本地 invoke 构建路径覆盖完整（build-all/build-tvm/nuitka-*/build-wheel/verify）
- [x] [AC-6] wheel 验证标准覆盖完整（9 项测试 + auditwheel + 依赖解析）
- [x] [AC-7] CMake 打包原理覆盖完整（_libs/RPATH/数据目录/chmod）
- [x] [AC-8] AST 兼容层与 bootstrap 机制覆盖完整（Monkey-patch/pth/PREAMBLE/TVM_LIBRARY_PATH）
- [x] [AC-9] 常见问题排查表覆盖（Conda 超时/pip --user/--no-isolation/entrypoint su/LLVM 冲突等）

## 验证与交付（V/C 阶段）
- [x] [AC-10] 交叉引用相对路径有效，无断链
- [x] 通过 V 对抗审查（5 条意见，全部采纳修正）
- [x] 逐项核对 AC-1~AC-10 全部通过
