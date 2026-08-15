# devcontainer-base 变体 Dockerfile 重构优化 - 检查清单

> **版本**：v2.3（基于七概念方法论重新设计，Task 1-3已完成）
> **更新日期**：2026-08-15

## 实施阶段检查点

### 阶段一：补全框架基础设施
- [x] mirror.sh 已实现，支持4种conda源+性能参数 ✅
- [x] install-helpers.sh 已实现，conda/pip_install_group函数 ✅
- [x] ft-guards.sh 已实现，free-threading守卫函数 ✅
- [ ] cleanup.sh 已实现，安全清理（不碰计时器目录）
- [ ] build-info.sh 已实现，统一build-info写入
- [ ] verify.sh 已实现，基础验证函数
- [ ] permissions.sh 已实现，权限设置函数
- [ ] variant-framework.sh 入口脚本已实现，正确source顺序
- [ ] 所有9个新脚本+现有2个脚本共10个全部通过 bash -n 语法检查
- [ ] VARIANT_DEBUG=1 可正常启用调试输出

### 阶段二：向后兼容、测试与模板
- [ ] conda-mirror-setup.sh 已更新，内部调用mirror.sh保持向后兼容
- [ ] 框架集成测试通过：source variant-framework.sh 无错误，所有函数已定义
- [ ] _template/Dockerfile 已更新使用新框架
- [ ] 模板代码量 < 100行
- [ ] 模板可成功构建dummy变体验证框架可用性

### 阶段三：试点迁移
- [ ] conda-llvm 变体已迁移到新框架
- [ ] conda-llvm docker build成功
- [ ] conda-llvm所有验证项通过（LLVM版本、C++编译、free-threading）
- [ ] conda-llvm test-conda-llvm-smoke.sh全部通过
- [ ] conda-llvm代码量减少70%+（从593行→<180行）

### 阶段四：全变体迁移
- [ ] onnx-dev 迁移完成，纯ONNX冒烟测试通过，torch缺席检查通过
- [ ] onnx-pytorch 迁移完成，PyTorch CPU可用，ONNX导出通过
- [ ] onnx-quantized 迁移完成，量化测试通过
- [ ] ai-dev 迁移完成，transformers/Jupyter双kernel可用
- [ ] 所有变体代码量平均减少70%+

### 阶段五：全量验证
- [ ] build.sh --list 可正常列出所有变体
- [ ] 所有 test-*.sh 测试脚本100%通过
- [ ] 构建日志格式统一（[TIMER]标记、SUMMARY表格）
- [ ] 所有build-info文件存在且格式一致
- [ ] 所有变体镜像大小无显著增加（<5%）
- [ ] 无功能回归

---

## 七概念质量门（G1-G4）

- [x] **G1（事实）**：代码库现状已勘查：shared/lib已有logging.sh(237行)和timer.sh(204行)，设计优于原Spec；变体实际为5个（conda已下线）；所有事实无因果推断词 ✓
- [x] **G2（洞察）**：根因分析完成：框架完成度仅2/9≈22%、缺入口脚本、Spec与代码状态不同步；四元组（现象+根因+影响+建议）完整 ✓
- [x] **G3（模式）**：框架设计可复用：10模块单一职责、统一variant_前缀、与现有logging/timer风格一致；反模式已在对抗审查中识别并规避 ✓
- [x] **G4（原子）**：任务拆分原子化：19个任务（8个框架+3个阶段二+1个试点+4个变体迁移+3个收尾），每个单一职责、可独立验证、依赖关系明确 ✓

---

## 关键设计决策确认

- [x] 保留现有logging.sh和timer.sh，不重写、不降级API
- [x] 计时器存储路径使用/root/.variant-timers/（与现有timer.sh一致，而非Spec原设计的/var/tmp/）
- [x] 每个RUN heredoc开头source框架（Docker每个RUN是独立shell，这是设计要求）
- [x] conda-mirror-setup.sh保留为独立可执行脚本，内部调用mirror.sh（向后兼容）
- [x] 迁移顺序按依赖拓扑：conda-llvm→onnx-dev→onnx-pytorch/onnx-quantized(可并行)→ai-dev
- [x] 变体数量更新为5个（原Spec7个，含已下线的conda）
- [x] 代码量减少目标从60%提升到70%（框架更完善，模板更精简）
