# devcontainer-base 镜像瘦身 - Pre-flight Checklist

> **2026-08-14 更新**：本 checklist 已同步 devcontainer-base v2.2/v2.2.1 实际演进状态。原始规划中的 5 镜像架构已被单镜像（Miniforge3 + Python 3.14.6 free-threading）架构取代；应用路径由 `apps/devcontainer-base/` 变更为 `apps/docker-images/devcontainer-base/`。

## G3 规范符合性自检
- [x] 已读取AGENTS.md启动协议
- [x] 已完成内容敏感度预检：本项目为公开内容（DevOps/基础设施代码）
- [x] 已通过I阶段洞察：镜像层体积分析完成，根因明确
- [x] 已通过F阶段第一性原理：7条公理推导完成，瘦身策略有理论依据；v2.2 进一步以 F→V→I 链路推导构建流水线优化
- [x] 任务原子化拆分：9个独立Task，依赖关系清晰
- [x] 验收标准可验证：11个AC（9个rule + 2个rubric），均有明确Pass Condition和Evidence

## 风险评估（更新后）

| 风险项 | 影响 | 概率 | 缓解措施 | 当前状态 |
|--------|------|------|----------|---------|
| LLVM strip后Nuitka编译失败 | 高 | 低 | strip只做--strip-unneeded，保留必要符号；v2.2 已验证 clang/lld/cmake/ninja 命令可用 | ✅ 已通过 |
| 删除include/静态库影响下游编译 | 高 | 中 | conda-llvm是最终变体？不，onnx-pytorch FROM conda-llvm但onnx-pytorch装的是预编译wheel，不需要编译；xmnn-whl-builder需要编译，已验证其Dockerfile | ✅ 已缓解 |
| 移除/opt/venv破坏下游路径引用 | 中 | 中 | 检查所有下游Dockerfile是否引用/opt/venv；entrypoint和supervisord配置同步更新 | ✅ 已安全移除 |
| 基础镜像体积目标无法达成 | 中 | 低 | 实际2.46GB，单镜像覆盖原 base+conda 两层能力 | ✅ 主镜像已验证 |
| conda清理过度导致包损坏 | 中 | 低 | conda clean只删缓存，不删已安装包；v2.2 验证所有命令运行正常 | ✅ 已通过 |
| 变体镜像基于新基础运行时兼容性问题 | 高 | 中 | Dockerfile 已适配，但 conda-llvm/onnx-pytorch/onnx-quantized 运行时验证待执行（Task 8） | ⏳ 待验证 |
| Python 3.14 wheel 生态不成熟 | 中 | 高 | PyTorch/ONNX 可能无 Python 3.14 wheel，CI 中变体构建标记为 experimental(continue-on-error) | ⏳ 生态待确认 |

## 前置依赖检查
- [x] Docker daemon可启动（ensure-wsl-docker.sh可用）
- [x] 当前devcontainer-base镜像已在本地构建，可作为对比基准
- [x] 所有相关Dockerfile路径已确认（新路径 apps/docker-images/devcontainer-base/）
- [x] 已读取当前所有Dockerfile完整内容（Task 1-6 执行时完成）

## 执行前确认
- [x] 用户已审批spec.md和tasks.md
- [x] 确认xmnn-whl-builder等下游应用的Dockerfile不硬依赖/opt/venv（已验证）
- [x] 确认onnx-pytorch/onnx-quantized不需要编译C++扩展（使用预编译wheel）
- [x] v2.2 主镜像构建验证通过（11/11深度验证）
- [x] v2.2.1 Stage 4 优化验证通过（419s→37s缓存热构建）
- [x] C扩展模板容器内验证通过（8线程×100K压力测试无竞态）
- [ ] 变体镜像（conda-llvm/onnx-pytorch/onnx-quantized）运行时验证（Task 8 待执行）