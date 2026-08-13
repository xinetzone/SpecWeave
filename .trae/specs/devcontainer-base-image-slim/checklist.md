# devcontainer-base 镜像瘦身 - Pre-flight Checklist

## G3 规范符合性自检
- [x] 已读取AGENTS.md启动协议
- [x] 已完成内容敏感度预检：本项目为公开内容（DevOps/基础设施代码）
- [x] 已通过I阶段洞察：镜像层体积分析完成，根因明确
- [x] 已通过F阶段第一性原理：7条公理推导完成，瘦身策略有理论依据
- [x] 任务原子化拆分：8个独立Task，依赖关系清晰
- [x] 验收标准可验证：10个AC（8个rule + 2个rubric），均有明确Pass Condition和Evidence

## 风险评估
| 风险项 | 影响 | 概率 | 缓解措施 |
|--------|------|------|----------|
| LLVM strip后Nuitka编译失败 | 高 | 低 | strip只做--strip-unneeded，保留必要符号；Task 5验证clang命令可用 |
| 删除include/静态库影响下游编译 | 高 | 中 | conda-llvm是最终变体？不，onnx-pytorch FROM conda-llvm但onnx-pytorch装的是预编译wheel，不需要编译；xmnn-whl-builder需要编译，验证它的Dockerfile |
| 移除/opt/venv破坏下游路径引用 | 中 | 中 | 检查所有下游Dockerfile是否引用/opt/venv；entrypoint和supervisord配置同步更新 |
| 基础镜像体积目标无法达成 | 中 | 低 | Docker CE本身322MB，系统必要包~200MB，留有余量 |
| conda清理过度导致包损坏 | 中 | 低 | conda clean只删缓存，不删已安装包；验证所有命令运行正常 |

## 前置依赖检查
- [x] Docker daemon可启动（ensure-wsl-docker.sh可用）
- [x] 当前devcontainer-base镜像已在本地构建，可作为对比基准
- [x] 所有相关Dockerfile路径已确认
- [ ] 需要先读取当前所有Dockerfile完整内容（Task 1执行时完成）

## 执行前确认
- [ ] 用户已审批spec.md和tasks.md
- [ ] 确认xmnn-whl-builder等下游应用的Dockerfile不硬依赖/opt/venv
- [ ] 确认onnx-pytorch/onnx-quantized不需要编译C++扩展（使用预编译wheel）
