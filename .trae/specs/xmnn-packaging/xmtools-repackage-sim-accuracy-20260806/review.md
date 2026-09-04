# xmtools 重新打包 + hub/caffe+onnx 仿真精度测试 - Verification Checklist

## 环境与构建

- [ ] Docker daemon 在 WSL 中正常运行（`docker ps` 无错误）
- [ ] xmtools、npu_tvm、npuusertools 三个兄弟目录存在且完整
- [ ] 开发镜像 `xmnn-dev:llvm22` 存在（或已成功构建）
- [ ] `xmtools/build/` 目录已创建用于存放产出物
- [ ] xmnn wheel 构建成功（`build-and-test.sh --no-build` exit 0）
- [ ] wheel 文件存在于 `dist/` 目录，大小 ~160-200MB
- [ ] 构建日志包含 `tvm.build(llvm) compute test: PASS`
- [ ] pyproject.toml 在构建后已恢复原状
- [ ] 运行时镜像 `xmnn:1.2.1-sim-accuracy` 构建成功（`build-runtime.sh` exit 0）
- [ ] `docker run --rm xmnn:1.2.1-sim-accuracy` 输出 XMNN runtime ready 且无报错

## 模型枚举与配置

- [ ] enumerate_hub.py 成功列出所有 hub/caffe 和 hub/onnx 完整产物模型
- [ ] 模型清单保存到 `build/hub_models_list.txt`
- [ ] 不完整模型已识别并记录
- [ ] patch_to_sim.py 已扩展支持 hub/caffe 和 hub/onnx
- [ ] hub/caffe 和 hub/onnx 所有 config.toml 已备份到 `build/hub_config_backup/`
- [ ] 备份文件数量等于 hub/caffe + hub/onnx config.toml 总数
- [ ] patch 后所有 config.toml 的 `[compile]` 段 target 为 `"sim_vta2.0"`
- [ ] patch 后所有 config.toml 的 `[compile]` 段 tune 为 `false`
- [ ] patch 未误改 `[model]`/`[inference]` 等其他段

## 批量编译

- [ ] 批量编译编排脚本 `run_hub_sim_tests.py` 已创建
- [ ] 所有清单中的模型均被尝试编译（无遗漏）
- [ ] 单模型编译失败不影响后续模型执行（容错生效）
- [ ] 编译日志按模型名保存到 `build/compile_logs/`
- [ ] `build/compile_success.txt` 记录了所有编译成功模型
- [ ] `build/compile_failed.txt` 记录了所有编译失败模型及错误摘要
- [ ] 编译成功模型的 `network.xmnn` 和 `param.bin` 存在

## 批量精度测试

- [ ] 所有编译成功模型均被尝试精度测试
- [ ] 精度测试日志按模型名保存到 `build/accuracy_logs/`
- [ ] 精度测试成功模型的 result.csv 收集到 `build/accuracy_results/<model>/`
- [ ] result.csv 包含余弦相似度、MSE、MAE 等精度指标
- [ ] `build/accuracy_failed.txt` 记录了精度测试失败模型及原因

## 报告

- [ ] 精度报告 `build/xmnn-hub-caffe-onnx-sim-accuracy-report.md` 已生成
- [ ] 报告包含环境信息（wheel版本、镜像标签、构建时间、Python/TVM版本）
- [ ] 报告包含完整的模型精度汇总表格（模型名 | 前端 | 编译状态 | 精度状态 | 余弦相似度 | MSE | MAE | 备注）
- [ ] 报告模型总数 = 编译成功 + 编译失败 = 枚举总数
- [ ] 编译失败模型及原因分类清晰
- [ ] 精度异常值（余弦相似度 < 0.99）已标注
- [ ] 报告结构清晰、可读

## 清洁与恢复

- [ ] 所有 hub config.toml 已从备份恢复
- [ ] 在 xmtools 子模块内 `git status` 不显示 config.toml 为 modified
- [ ] `git diff -- models/hub/` 无输出
- [ ] 抽查 config.toml 确认 target 恢复为原始值
- [ ] 运行时容器已正确退出（无残留）
- [ ] build/ 目录产物完整保留（日志、报告、结果）
