# Caffex 算子库 Docker 环境全面测试与标准化报告生成 - Verification Checklist

## 环境预检
- [ ] 检查点1: Docker Desktop 运行中，`docker info` 正常返回
- [ ] 检查点2: `caffe-cpu:origin-runtime` 镜像存在（或 build.sh 可成功构建）
- [ ] 检查点3: 容器内 `verify-caffe.sh` 12项检查全部通过（退出码0）
- [ ] 检查点4: 容器内 `import caffe` 成功，版本信息正常输出
- [ ] 检查点5: 容器与宿主机目录挂载可读写（tests/ops/ 挂载正常）

## 测试运行脚本适配
- [ ] 检查点6: 运行脚本结果目录正确指向 `tests/.temp/`（非 docker/origin/test-results/）
- [ ] 检查点7: 每次运行在 .temp/ 下创建独立时间戳子目录，避免覆盖
- [ ] 检查点8: 脚本支持 correctness/edge/performance/all 四种测试类型
- [ ] 检查点9: 容器内自动安装 pytest/pytest-cov 依赖（使用阿里云镜像源）
- [ ] 检查点10: 环境变量（PYTHONPATH/LD_LIBRARY_PATH/GLOG_minloglevel）正确设置
- [ ] 检查点11: stdout/stderr 完整捕获到日志文件
- [ ] 检查点12: 脚本错误处理完善，测试失败不阻止后续步骤和报告生成

## 功能正确性测试执行
- [ ] 检查点13: correctness 类型测试运行完成（pytest -m "correctness and not slow"）
- [ ] 检查点14: junit_correctness.xml 文件生成且为有效XML
- [ ] 检查点15: log_correctness.txt 包含完整测试输出
- [ ] 检查点16: 执行耗时被记录

## 边界条件测试执行
- [ ] 检查点17: edge 类型测试运行完成（pytest -m "edge"）
- [ ] 检查点18: junit_edge.xml 文件生成且为有效XML
- [ ] 检查点19: log_edge.txt 包含完整测试输出
- [ ] 检查点20: 所有带 @pytest.mark.edge 标记的测试用例被执行

## 性能基准测试执行
- [ ] 检查点21: slow/performance 类型测试运行完成（pytest -m "slow"）
- [ ] 检查点22: junit_performance.xml 文件生成
- [ ] 检查点23: log_performance.txt 包含性能计时数据（如存在性能测试）
- [ ] 检查点24: 若不存在slow标记测试，在结果中明确记录"无专项性能测试"

## 全量兼容性测试执行
- [ ] 检查点25: all 类型测试运行完成（pytest 无marker过滤）
- [ ] 检查点26: junit_all.xml 文件生成且为有效XML
- [ ] 检查点27: log_all.txt 包含完整测试输出
- [ ] 检查点28: 32个测试文件全部被pytest发现并执行（无遗漏）

## 报告生成脚本
- [ ] 检查点29: generate_report.py 脚本存在且可运行（宿主Python 3.13+）
- [ ] 检查点30: 脚本可正确解析JUnit XML格式（使用xml.etree.ElementTree）
- [ ] 检查点31: 统计数据计算正确（total=pass+fail+error+skip）
- [ ] 检查点32: 脚本健壮性：缺失XML/日志文件时不崩溃，给出提示
- [ ] 检查点33: 脚本不依赖第三方包（仅使用Python标准库）

## 标准化测试报告
- [ ] 检查点34: OPS_TEST_REPORT.md 生成在 tests/.temp/<timestamp>/ 下
- [ ] 检查点35: 报告包含「测试元信息」章节（时间、镜像、环境、复现命令）
- [ ] 检查点36: 报告包含「执行摘要」章节（总用例数、通过/失败/错误/跳过、通过率、总耗时）
- [ ] 检查点37: 报告包含「分类型结果」章节（correctness/edge/performance各自通过率）
- [ ] 检查点38: 报告包含「算子维度汇总」章节（每个算子的测试状态表格）
- [ ] 检查点39: 报告包含「性能基准表」章节（有性能数据时给出排名表，无数据时说明）
- [ ] 检查点40: 报告包含「失败用例详情」章节（失败测试名、错误消息、traceback摘要）
- [ ] 检查点41: 报告包含「边界条件测试覆盖」章节
- [ ] 检查点42: 报告包含「兼容性测试说明」章节（多形状/多维度覆盖情况）
- [ ] 检查点43: 报告包含「问题清单与初步分析」章节
- [ ] 检查点44: 报告包含「附录」章节（原始日志路径、完整复现命令）
- [ ] 检查点45: 报告统计数据与JUnit XML原始数据一致（抽查3-5个用例核对）
- [ ] 检查点46: 报告主体为中文，技术术语保留英文
- [ ] 检查点47: 报告Markdown格式正确（表格对齐、代码块标注、标题层级正确）

## 输出目录与可复现性
- [ ] 检查点48: tests/.temp/<timestamp>/ 目录结构完整（包含所有XML、日志、报告文件）
- [ ] 检查点49: env_info.txt 包含Python/numpy/protobuf/caffe版本信息
- [ ] 检查点50: 报告中的复现命令可直接复制执行（语法正确）
- [ ] 检查点51: LATEST.txt（或等效索引）指向最新结果目录
- [ ] 检查点52: README.md 说明目录内容和复现方法
- [ ] 检查点53: 所有文件路径使用相对路径或明确绝对路径说明
- [ ] 检查点54: caffex/ 目录下的BVLC原始源码未被修改
