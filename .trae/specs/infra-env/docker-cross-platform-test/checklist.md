# Docker跨平台构建测试 - Verification Checklist

## 调研与设计阶段
- [ ] conda-forge cross-compilation调研完成，输出cross-toolchain包名、conda_build_config.yaml模板
- [ ] scikit-build-core cross-compile平台检测行为已确认（build vs host）
- [ ] Wine运行Windows conda可行性已确认（或已决策降级为L2 only）
- [ ] MSVC vs MinGW ABI选择已决策并记录理由
- [ ] Open Questions Q1-Q6均已回答或标记为待验证

## conda recipe改造
- [ ] conda_build_config.yaml创建并正确配置osx-64/osx-arm64/win-64
- [ ] meta.yaml build/host/run依赖正确分离，cross-selector使用正确
- [ ] build.sh检测CONDA_BUILD_CROSS_COMPILATION并跳过host Python import
- [ ] build.sh在cross-compile时使用正确的静态二进制分析工具
- [ ] Linux原生构建回归测试通过（无cross-compile时行为不变）
- [ ] meta.yaml lint/conda-verify检查通过

## macOS cross-compile Docker镜像
- [ ] Dockerfile.cross-macos基于现有caffe-ffi-jupyter镜像扩展
- [ ] osx-64和osx-arm64 cross-toolchain安装成功
- [ ] macos-sdk和cctools/ld64安装成功
- [ ] x86_64-apple-darwin-clang++可用且版本正确
- [ ] llvm-otool/llvm-nm/llvm-install-name-tool可用
- [ ] conda build osx-64成功产出.dylib文件
- [ ] .dylib文件类型验证为Mach-O 64-bit
- [ ] 镜像大小<5GB（或记录超标原因）
- [ ] 独立cross-build conda环境不污染主环境

## Windows cross-compile + Wine Docker镜像
- [ ] Dockerfile.cross-windows基于现有caffe-ffi-jupyter镜像扩展
- [ ] win-64 cross-toolchain安装成功
- [ ] Wine安装并配置正确（Windows 10 prefix）
- [ ] Windows版Miniconda/Miniforge在Wine中安装成功
- [ ] win-64 numpy在Wine中import成功（基础环境验证）
- [ ] conda build win-64成功产出.pyd文件
- [ ] .pyd文件类型验证为PE32+ executable DLL
- [ ] wine-python/wine-conda辅助脚本可用

## test-cross-build.sh测试脚本
- [ ] --target参数解析正确（osx-64/osx-arm64/win-64/all）
- [ ] --test-level参数解析正确（1/2/3）
- [ ] --skip-runtime参数正确跳过L3
- [ ] L1层：conda build成功，检查输出文件存在和类型
- [ ] L2层macOS：llvm-otool检查依赖、llvm-nm检查符号、RPATH验证
- [ ] L2层Windows：objdump检查PE导入表、符号验证
- [ ] L2层：RPATH不包含build prefix绝对路径
- [ ] L2层：TVMFFIGetCustomAllocator符号存在（T类型）
- [ ] L3层macOS：输出skip信息并返回特殊码（非失败）
- [ ] L3层Windows：Wine中conda install + import测试
- [ ] 结构化测试报告输出（PASS/FAIL/ERROR）
- [ ] 退出码正确（全0通过=0，任何失败=1）
- [ ] 脚本风格与现有test-conda-build.sh一致

## Docker Compose编排
- [ ] docker-compose.yml新增cross-build服务
- [ ] TARGET_PLATFORM参数支持
- [ ] SpecWeave卷挂载正确共享
- [ ] docker compose build成功
- [ ] docker compose run cross-build --target=all --test-level=2执行成功
- [ ] 一次性任务容器（无端口暴露、无restart）

## 文档更新
- [ ] l4-verification-plan-and-checklist.md更新：A-T2/A-T5标记验证方式
- [ ] 跨平台测试覆盖矩阵新增
- [ ] conda-build-scikit-build-core-native模式文档新增cross-compile章节
- [ ] conda_build_config.yaml模板和build.sh适配要点文档化
- [ ] README.md更新cross-build测试状态
- [ ] 模式文档V2质量检查通过（pre-commit hook）
- [ ] 已知限制和待真实机器验证的项清晰记录

## 端到端验证
- [ ] osx-64 L1+L2端到端PASS
- [ ] osx-arm64 L1+L2端到端PASS（或blocker记录）
- [ ] win-64 L1+L2端到端PASS
- [ ] win-64 L3端到端PASS或预期失败+原因
- [ ] Linux原生test-conda-build.sh回归测试全部PASS
- [ ] 现有caffe-ffi-jupyter服务（Jupyter/SSH/editable install）不受影响
- [ ] 原子提交完成（代码+文档+子模块）
