# Tasks: ai-dev 变体萃取

## Task 1: 创建变体目录结构
- 创建 `variants/ai-dev/` 目录
- 创建 `variants/ai-dev/.agents/rules/` 目录
- 状态：pending

## Task 2: 编写 Dockerfile
- 文件：`variants/ai-dev/Dockerfile`
- 基于 `_template/` 和 `onnx-quantized/Dockerfile` 模式
- 3 层追加阶段：
  - Stage 1/3: 基础验证 + 计时器初始化
  - Stage 2/3: Python 包安装（50+包，PIP_USER=0，缓存挂载）
  - Stage 3/3: Jupyter内核注册 + build-info + 清理 + [VALIDATION CHECKPOINT] + 计时汇总
- 不覆盖 ENTRYPOINT/CMD/WORKDIR
- 状态：pending
- 验收：
  - [ ] 首行 syntax 声明
  - [ ] FROM 后有 SHELL 重置
  - [ ] 3个阶段都有 [TIMER] 标记
  - [ ] 末尾有 [VALIDATION CHECKPOINT]
  - [ ] 有 build-info 写入
  - [ ] 无 ENTRYPOINT/CMD/WORKDIR 覆盖

## Task 3: 创建 .env.example
- 文件：`variants/ai-dev/.env.example`
- 包含 BASE_TAG, APT_MIRROR, CONDA_MIRROR, PIP_MIRROR
- 状态：pending

## Task 4: 创建 .agents/rules/dockerfile.md
- 文件：`variants/ai-dev/.agents/rules/dockerfile.md`
- 记录变体特有规范
- 状态：pending

## Task 5: 创建 README.md
- 文件：`variants/ai-dev/README.md`
- 完整使用文档
- 状态：pending

## Task 6: 注册到 build.sh
- 文件：`variants/build.sh`
- 在 VARIANTS 数组中添加 ai-dev 条目
- 格式：`ai-dev|描述|onnx-quantized|验证命令`
- 验证命令用 `;` 分隔
- 状态：pending
- 验收：
  - [ ] `bash build.sh --list` 显示 ai-dev
  - [ ] 依赖显示为 onnx-quantized
  - [ ] VARIANTS 数组格式正确（`|` 分隔）

## Task 7: 注册到 variants/README.md
- 文件：`variants/README.md`
- 在可用变体表格中添加 ai-dev 行
- 状态：pending

## Task 8: 创建测试脚本
- 文件：`variants/scripts/test-ai-dev.sh`
- 遵循 testing.md 的 L1-L6 分层策略
- 至少 15 个测试用例
- 状态：pending
- 验收：
  - [ ] L1: 工具链版本检查
  - [ ] L2: 功能测试（包导入+操作）
  - [ ] L3: 深度组件验证（2+）
  - [ ] L4: 5项基础服务继承
  - [ ] L5: PATH优先级
  - [ ] L6: 配置文件验证
  - [ ] 脚本通过 bash -n 语法检查

## Task 9: 最终验证
- 所有文件创建完成
- Dockerfile 语法检查
- Shell 脚本语法检查
- 文档链接有效性检查
- 状态：pending

## 依赖关系
```
Task 1 → Task 2,3,4,5（目录结构先行）
Task 2,3,4,5 → Task 6,7（文件就绪后注册）
Task 6 → Task 8（注册后测试）
Task 2,3,4,5,6,7,8 → Task 9（全部完成后最终验证）
```
