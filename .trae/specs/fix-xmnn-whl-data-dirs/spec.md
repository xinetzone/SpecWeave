# xmnn whl 打包数据目录修复 Spec

## Why
xmnn-client:1.2.2-alpha 镜像中，autolibs/、fonts/、tools_cpp/ 三个数据目录未被打包进 xmnn whl，导致运行时缺失必要的自动调优日志、字体和 C++ 部署工具。同时 vta_hw/ 目录打包了过多内容，实际只需要 config/ 子目录。

## What Changes
- 修复 packaging/CMakeLists.txt：为数据目录 install(DIRECTORY ...) 添加存在性检查，确保目录不存在时构建失败
- 修复 packaging/vta/CMakeLists.txt：将 install(DIRECTORY .../vta_hw/ ...) 改为只安装 vta_hw/config/
- 强化 src/xmpack/wheel.py：在 wheel 验证脚本中增加对数据目录的完整性检查

## Impact
- Affected specs: 无
- Affected code:
  - packaging/CMakeLists.txt
  - packaging/vta/CMakeLists.txt
  - src/xmpack/wheel.py

## ADDED Requirements

### Requirement: CMake 数据目录安装前存在性检查
系统 SHALL 在 CMake configure 阶段检查 autolibs/、fonts/、tools_cpp/ 源目录是否存在，若不存在则报 FATAL_ERROR 终止构建。

#### Scenario: 数据目录存在
- **WHEN** XMNN_DATA_DIR 指向的路径下存在 autolibs/、fonts/、tools_cpp/ 子目录
- **THEN** CMake 正常安装这些目录到 wheel 的 site-packages 根目录

#### Scenario: 数据目录缺失
- **WHEN** XMNN_DATA_DIR 指向的路径下缺少任意一个数据子目录
- **THEN** CMake 报 FATAL_ERROR 并明确指出缺失的目录路径，终止构建

### Requirement: vta_hw 仅打包 config 子目录
系统 SHALL 仅将 vta_hw/config/ 打包进 whl，而非整个 vta_hw/ 目录。

#### Scenario: vta_hw 目录含多余内容
- **WHEN** vta_hw/ 目录下除了 config/ 外还有其他子目录
- **THEN** wheel 中仅包含 vta_hw/config/（含 pkg_config.py、vta_config.json 等文件）

### Requirement: Wheel 验证覆盖数据目录完整性
系统 SHALL 在 wheel 打包后的验证阶段检查数据目录是否存在。

#### Scenario: 数据目录缺失
- **WHEN** wheel 打包完成但 autolibs/、fonts/、tools_cpp/ 或 vta_hw/config/ 缺失
- **THEN** 验证脚本报错并终止，输出缺失目录列表

## MODIFIED Requirements

### Requirement: vta_hw 安装逻辑
系统 SHALL 将 install(DIRECTORY .../vta_hw/ DESTINATION vta_hw) 修改为 install(DIRECTORY .../vta_hw/config/ DESTINATION vta_hw/config)。

#### Scenario: 仅 config 子目录被安装
- **WHEN** VTA artifacts 目录包含 vta_hw/config/ 和其他子目录
- **THEN** 仅 vta_hw/config/ 的内容被安装到 wheel 的 vta_hw/config/ 路径