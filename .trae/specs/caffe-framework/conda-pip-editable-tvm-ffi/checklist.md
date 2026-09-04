# caffe-ffi Conda pip-install tvm-ffi 集成 - Verification Checklist

## 构建与安装
- [x] conda build conda.recipe/ 在 Docker 容器中成功完成（无错误退出）
- [x] 生成的 .conda 包文件大小合理（caffe-ffi + tvm-ffi 两个包的总和，约 2.7 MB）
- [x] conda install --use-local caffe-ffi 成功安装，无 SafetyError/ClobberError
- [x] 安装后 $SP_DIR/ 下同时存在 caffe_ffi/ 和 tvm_ffi/ 两个目录

## tvm-ffi 安装验证
- [x] tvm_ffi 从本地源码安装（非 PyPI wheel），nm -D $SP_DIR/tvm_ffi/lib/libtvm_ffi.so 包含 TVMFFIGetCustomAllocator 符号（T 类型，地址 0xb23a0）
- [x] tvm_ffi 非 editable 安装：从 site-packages/tvm_ffi/__init__.py 加载
- [x] `python -m tvm_ffi.config --cmakedir` 返回有效的 CMake 配置目录路径（CMake find_package 成功）

## Native 加载验证
- [x] `python -c "import caffe_ffi; print(caffe_ffi.is_available())"` 输出 True，无 Python-only fallback 警告
- [x] `python -c "from caffe_ffi import Blob; b = Blob([100]); b.fill(1.0); print(b.count())"` 输出 100
- [x] Blob.to_numpy() 返回 shape=(100,) dtype=float32 的数组，全为 1.0
- [x] caffe_ffi.version() 输出 0.1.0

## 共享库依赖验证
- [x] ldd $SP_DIR/caffe_ffi/_caffe_ffi.so 中 libtvm_ffi.so 解析到 $SP_DIR/tvm_ffi/lib/libtvm_ffi.so（通过 $ORIGIN/../tvm_ffi/lib）
- [x] ldd 输出中无 "not found" 依赖项
- [x] RPATH 包含 $ORIGIN/../tvm_ffi/lib 相对路径（通过 CMAKE_INSTALL_RPATH 设置）
- [x] RPATH 中无硬编码绝对路径（除 conda PREFIX 兜底路径外）

## CMake 依赖查找验证
- [x] 构建日志中 CMake 输出 "Found tvm-ffi CMake config via Python"（使用 find_package 模式）
- [x] 构建日志中无 "Auto-detected local tvm-ffi source"（未走 add_subdirectory 模式）

## 代码质量
- [x] build.sh 中已移除 libtvm_ffi.so 的手动复制逻辑
- [x] Dependencies.cmake 中 find_package 和 add_subdirectory 两条路径清晰互斥（CAFFE_FFI_PREFER_SYSTEM_TVM_FFI 选项控制）
- [x] SKBUILD_CMAKE_ARGS 使用空格分隔（非分号），避免 CMake 列表解析错误
- [x] pip install 时临时清空 conda 的 CMAKE_ARGS，避免 -DCMAKE_INSTALL_PREFIX 干扰 wheel 构建

## 回退模式验证
- [x] 当本地 vendor/tvm-ffi 不可用时，build.sh 回退到 pip install apache-tvm-ffi 模式（代码逻辑保留）
- [ ] 回退模式下构建可完成（未测试，核心路径已验证）

## 清理脚本验证
- [x] full-clean-rebuild.sh 正确清理 site-packages 中的 tvm_ffi/ 残留和 caffe_ffi/ 残留
- [x] full-clean-rebuild.sh 正确清理 conda-bld 缓存和 conda 包缓存
- [x] full-clean-rebuild.sh 正确清理 _editable_*.pth 文件和指向源码目录的 .pth 文件

## conda-build test 阶段
- [x] 包安装后手动验证 imports caffe_ffi 和 tvm_ffi 通过
- [x] 包安装后手动验证 is_available() = True
- [x] 包安装后手动验证 Blob 功能测试通过
