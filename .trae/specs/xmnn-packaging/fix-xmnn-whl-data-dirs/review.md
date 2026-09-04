# Checklist

- [x] packaging/CMakeLists.txt 中 autolibs/ 安装前有存在性检查，不存在时报 FATAL_ERROR
- [x] packaging/CMakeLists.txt 中 fonts/ 安装前有存在性检查，不存在时报 FATAL_ERROR
- [x] packaging/CMakeLists.txt 中 tools_cpp/ 安装前有存在性检查，不存在时报 FATAL_ERROR
- [x] packaging/vta/CMakeLists.txt 中 install(DIRECTORY ...) 仅安装 vta_hw/config/ 而非整个 vta_hw/
- [x] src/xmpack/wheel.py 的 wheel 验证脚本中包含对 autolibs/ 目录的存在性检查
- [x] src/xmpack/wheel.py 的 wheel 验证脚本中包含对 fonts/ 目录的存在性检查
- [x] src/xmpack/wheel.py 的 wheel 验证脚本中包含对 tools_cpp/ 目录的存在性检查
- [x] src/xmpack/wheel.py 的 wheel 验证脚本中包含对 vta_hw/config/ 目录的存在性检查