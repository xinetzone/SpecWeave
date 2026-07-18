# 导出建议

## 可复用模式

### 模式名称：精确符号可见性控制模式

**模式类型**：架构/构建

**抽象层次**：L2（方法）

**触发场景**：
- 静态链接第三方库的共享库项目
- 需要与其他可能包含相同依赖的共享库共存
- 使用静态初始化注册机制的项目

**核心步骤**：

1. **识别依赖类型**：确认项目是否静态链接第三方库（如 LLVM、OpenCV 等）
2. **选择符号控制方式**：
   - 优先使用 `-Wl,--exclude-libs,ALL`（仅隐藏静态库符号）
   - 避免使用 `-fvisibility=hidden`（会影响主程序符号）
   - 禁用 `--gc-sections`（保护静态注册对象）
3. **配置构建系统**：在 CMakeLists.txt 或 Makefile 中添加链接器标志
4. **验证符号可见性**：使用 readelf/nm 检查共享库的符号表
5. **测试共存场景**：与可能产生冲突的其他库一起加载测试

**适用条件**：
- 项目使用共享库（.so/.dll）形式发布
- 第三方库以静态库形式链接
- 项目使用静态初始化进行注册

**反模式**：
- 使用 `-fvisibility=hidden` 而不标记导出符号
- 启用 `--gc-sections` 优化
- 通过禁用功能来绕过符号冲突

**迁移验证记录**：
- 验证1：TVM 重新编译成功（884编译单元）
- 验证2：符号表分析确认 LLVM 符号隐藏
- 验证3：TVM+PyTorch 共存测试通过

**成熟度**：验证中（validation_count=3）

## 知识沉淀

### 链接器符号控制选项速查表

| 选项 | 作用 | 适用场景 | 注意事项 |
|------|------|---------|---------|
| `-Wl,--exclude-libs,ALL` | 将静态库符号标记为 LOCAL | 隐藏第三方依赖符号 | 不影响主程序符号 |
| `-fvisibility=hidden` | 默认隐藏所有符号 | 需要精确控制导出符号 | 需要配合 __attribute__((visibility("default"))) |
| `-Wl,--gc-sections` | 删除未引用的段 | 减小可执行文件大小 | 会删除静态注册对象 |
| `-Wl,--whole-archive` | 包含静态库所有段 | 保护静态注册对象 | 可能导致符号重复 |
| `-Wl,--no-undefined` | 禁止未定义符号 | 确保链接完整性 | 需要所有依赖都已链接 |

### TVM 构建配置最佳实践

```cmake
# 推荐配置
set(HIDE_PRIVATE_SYMBOLS ON)
# 启用 --exclude-libs,ALL 隐藏静态库符号
# 不使用 -fvisibility=hidden（保护 TVM_REGISTER_GLOBAL）
# 不使用 --gc-sections（保护静态注册对象）

# 禁用以下选项
# set(USE_LTO ON)  # LTO 会优化掉静态注册代码
```

### 符号冲突诊断流程

```
段错误或运行时崩溃
    ↓
检查是否加载了多个包含相同依赖的库
    ↓
使用 readelf -s 检查共享库符号表
    ↓
确认是否有重复的全局符号（如 LLVM、OpenCV 等）
    ↓
使用 --exclude-libs,ALL 隐藏静态库符号
    ↓
重新编译并测试共存场景
```

## 输出归档

### 已修改文件清单

| 文件路径 | 修改类型 | 说明 |
|----------|---------|------|
| external/xmhub/npu_tvm/CMakeLists.txt | 修改 | HIDE_PRIVATE_SYMBOLS 默认值和实现逻辑 |
| external/xmhub/npu_tvm/cmake/config.cmake | 修改 | 默认值和注释更新 |
| external/xmhub/npu_tvm/tasks.py | 修改 | use_hide_symbols 默认值改为 True |
| external/xmhub/dev-env/rebuild_tvm_codegenc.sh | 修改 | CMake 参数更新 |
| external/xmhub/npu_tvm/docker/local/nuitka/tvm/CMakeLists.txt | 修改 | 移除 libtvm_allvisible.so 引用 |
| external/xmhub/npu_tvm/docker/local/nuitka/compile.sh | 修改 | 移除 libtvm_allvisible.so 复制 |
| external/xmhub/npu_tvm/ci/jenkins/data.py | 修改 | 移除 tvm_allvisible 产物条目 |
| external/xmhub/npu_tvm/docs/install/from_source.rst | 修改 | 更新 HIDE_PRIVATE_SYMBOLS 文档 |

### 验证证据

1. **编译日志**：Docker 容器内编译成功，884编译单元，6.3分钟
2. **符号表分析**：readelf 输出显示 LLVM 符号隐藏，TVM 符号正常导出
3. **共存测试**：TVM+PyTorch 2.13.0+cu130 导入和 relay.build 测试通过

### 后续跟进

1. 监控新构建的 TVM 在实际项目中的表现
2. 收集用户反馈，确认修复效果
3. 在其他项目中推广精确符号控制模式

