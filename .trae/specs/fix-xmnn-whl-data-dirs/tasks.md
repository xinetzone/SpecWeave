# Tasks

- [x] Task 1: 修复 packaging/CMakeLists.txt — 数据目录安装前存在性检查
  - [x] 1.1: 在 autolibs/ install 前添加 `if(NOT EXISTS ...)` 检查，不存在时 `message(FATAL_ERROR ...)`
  - [x] 1.2: 在 fonts/ install 前添加同样的存在性检查
  - [x] 1.3: 在 tools_cpp/ install 前添加同样的存在性检查

- [x] Task 2: 修复 packaging/vta/CMakeLists.txt — vta_hw 仅安装 config/
  - [x] 2.1: 将 `install(DIRECTORY "${_VTA_ARTIFACTS_DIR}/vta_hw/" DESTINATION vta_hw)` 改为 `install(DIRECTORY "${_VTA_ARTIFACTS_DIR}/vta_hw/config/" DESTINATION vta_hw/config)`

- [x] Task 3: 强化 src/xmpack/wheel.py — wheel 验证阶段增加数据目录完整性检查
  - [x] 3.1: 在已有的 wheel 内容验证步骤（WHEEL_PLATLIB 区域）中，增加对 autolibs/、fonts/、tools_cpp/、vta_hw/config/ 四个目录的存在性检查，缺失时输出错误并 exit 1

# Task Dependencies
- Task 1、Task 2、Task 3 相互独立，可并行执行