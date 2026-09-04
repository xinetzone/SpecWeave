# Tasks

## Task 1: 创建 onnx-pytorch 变体目录结构
- [ ] 基于 `variants/conda-llvm` 复制并创建 `variants/onnx-pytorch/` 目录
- [ ] 创建 `Dockerfile`：以 `FROM devcontainer-base:conda-llvm-${BASE_TAG}` 为起点，替换所有变体名占位符，FROM 后重新声明 ARG
- [ ] 创建 `.env.example`：含 BASE_TAG/APT_MIRROR/CONDA_MIRROR/PIP_MIRROR/镜像参数
- [ ] 创建 `README.md`：描述、构建/运行/验证命令、使用说明
- [ ] 创建 `.agents/rules/dockerfile.md`：记录变体特有规范

## Task 2: 编写 Dockerfile 安装逻辑
- [ ] Stage 1：conda 频道配置 + PATH + 计时器初始化
- [ ] Stage 2：在 conda base 环境安装 CPU 版 PyTorch（torch + torchvision，CPU 索引）
- [ ] Stage 3：安装 ONNX 生态（onnx, onnxruntime, onnx-simplifier, onnxoptimizer）+ 激活脚本/权限验证
- [ ] Stage 4：写入 build-info（含 torch/onnx/onnxruntime 实际版本）+ 清理 + 最终验证 + 计时器汇总
- [ ] 保留 `[TIMER]` 标记、`[VALIDATION CHECKPOINT]`、`--mount=type=cache` 缓存挂载

## Task 3: 注册到 build.sh
- [ ] 在 `variants/build.sh` 的 `VARIANTS` 数组中新增 `onnx-pytorch` 条目，依赖 `conda-llvm`
- [ ] 定义验证命令（torch/onnx/onnxruntime 导入 + 版本输出）
- [ ] 执行 `bash variants/build.sh --list` 确认注册成功

## Task 4: 创建测试脚本
- [ ] 创建 `variants/scripts/test-onnx-pytorch.sh`，覆盖 L1-L6 六层测试
  - [ ] L1: torch/onnx/onnxruntime/torchvision 版本检查
  - [ ] L2: PyTorch CPU 张量运算 + ONNX 模型导出/推理 Hello World
  - [ ] L3: 深度组件验证（torchvision 模型、onnxruntime session）
  - [ ] L4: 基础服务继承测试（ssh/supervisord/docker/jupyter/devuser）
  - [ ] L5: PATH 优先级与环境隔离验证
  - [ ] L6: build-info 与配置文件验证
- [ ] （可选）创建 `variants/scripts/build-onnx-pytorch.sh` 一键构建脚本

## Task 5: 更新 variants/README.md
- [ ] 在可用变体表格中添加 `onnx-pytorch` 条目（描述/基础镜像/包含组件）

## Task 6: 构建与验证
- [ ] `bash -n` 语法检查 Dockerfile 与脚本
- [ ] `bash variants/build.sh --variant onnx-pytorch --cn` 构建成功
- [ ] 运行 `bash variants/scripts/test-onnx-pytorch.sh` 全部 PASS
- [ ] 确认 build-info 中 torch/onnx/onnxruntime 版本已记录

# Task Dependencies
- [Task 1] 依赖 `conda-llvm` 变体已存在（含 base 镜像与 conda-llvm 镜像）
- [Task 2] 依赖 [Task 1]
- [Task 3] 依赖 [Task 1]
- [Task 4] 依赖 [Task 2]
- [Task 5] 依赖 [Task 1]
- [Task 6] 依赖 [Task 2][Task 3][Task 4][Task 5]（构建验证需先有 Dockerfile 与注册）
