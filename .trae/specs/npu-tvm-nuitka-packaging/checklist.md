# NPU TVM Nuitka 打包功能 - 验证清单

- [ ] Checkpoint 1: Nuitka 打包配置目录结构完整，包含 tvm/ 和 vta/ 子目录
- [ ] Checkpoint 2: TVM 打包配置文件齐全（pyproject.toml, CMakeLists.txt, _tvm_nuitka_init.py, tvm_nuitka_init.pth）
- [ ] Checkpoint 3: VTA 打包配置文件齐全（pyproject.toml, CMakeLists.txt）
- [ ] Checkpoint 4: VTA 的 pyproject.toml 正确声明对 TVM 的依赖（dependencies = ["tvm>=0.19.0"]）
- [ ] Checkpoint 5: Dockerfile 包含 Nuitka 和 scikit-build-core 的安装命令
- [ ] Checkpoint 6: Docker 镜像构建成功，容器内可导入 Nuitka 和 scikit-build-core
- [ ] Checkpoint 7: Nuitka 编译脚本执行成功，生成独立的 tvm.cpython-*.so 文件
- [ ] Checkpoint 8: Nuitka 编译脚本执行成功，生成独立的 vta.cpython-*.so 文件（依赖已编译的 TVM）
- [ ] Checkpoint 9: Wheel 打包脚本执行成功，生成独立的 tvm-*.whl 文件
- [ ] Checkpoint 10: Wheel 打包脚本执行成功，生成独立的 vta-*.whl 文件
- [ ] Checkpoint 11: VTA wheel 的 METADATA 正确声明对 TVM 的依赖
- [ ] Checkpoint 12: 安装 TVM wheel 后 TVM 模块可独立导入和使用
- [ ] Checkpoint 13: 安装 TVM 和 VTA wheel 后 VTA 模块可正常导入
- [ ] Checkpoint 14: 增量编译功能正常（检测 .so 已存在时跳过）
- [ ] Checkpoint 15: 产物完整性验证功能正常（缺少必要文件时报错）
- [ ] Checkpoint 16: **自包含性验证**：所有配置文件和脚本不包含对 `external/xmhub/notebook` 的任何引用
- [ ] Checkpoint 17: **依赖隔离验证**：wheel 包不依赖 notebook 项目中的任何模块或资源