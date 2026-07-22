# Tasks

- [ ] Task 1: 新增 `gen_proto.py` — 从 reference 复制自动化 proto 生成脚本
  - [ ] 复制 `external/ffi/tvm-book/tests/caffeproto/gen_proto.py` 到 `external/chaos/caffe/gen_proto.py`
  - [ ] 验证脚本路径引用正确（proto_dir、out_dirs 指向当前目录）

- [ ] Task 2: 同步 `protos/caffe.proto` — 确保 NormalizeParameter 定义一致
  - [ ] 对比 reference 和 target 的 `protos/caffe.proto`，将 target 缺失的 NormalizeParameter 消息定义和 norm_param 字段补全
  - [ ] 确保 LayerParameter 中 next available ID 注释正确

- [ ] Task 3: 新增 `python/` 工具模块 — 从 reference 复制 TVM Relax 和模型工具
  - [ ] 复制 `python/utils.py`（Conv2D、ConvTranspose2D、L2Norm）
  - [ ] 复制 `python/caffe_utils.py`（unity_struct、unity_inputs、convert_num_to_name）
  - [ ] 复制 `python/caffe_fuse.py`（fuse_network、BN+Scale 融合）
  - [ ] 复制 `python/test_l2norm.py`（L2 归一化测试套件）
  - [ ] 复制 `python/protos/caffe_pb2.py`（副本 proto 绑定）

- [ ] Task 4: 升级 `README.md` — 对齐 reference `index.md` 的文档结构
  - [ ] 新增 gen_proto.py 快速生成方式（方式一）
  - [ ] 新增"添加新算子（四步法）"章节
  - [ ] 保留并优化现有 conda 安装和 CMake 构建说明
  - [ ] 确保 Python 版本为 3.14（与之前升级一致）

- [ ] Task 5: 简化 `CMakeLists.txt` — 对齐 reference 的简洁风格
  - [ ] 用 `protobuf_generate_python` 替代自定义 `generate_proto_python()` 函数
  - [ ] 保持 CMake 最低版本 3.15（与 reference 一致）
  - [ ] 保留必要的调试信息输出

- [ ] Task 6: 验证升级 — 运行 gen_proto.py 和测试
  - [ ] 运行 `python gen_proto.py` 验证代码生成
  - [ ] 运行 `python test_l2norm.py` 验证 protobuf 测试通过
  - [ ] 验证 `python/caffe_pb2.py` 可正常导入

# Task Dependencies

- Task 2 依赖 Task 1（proto 同步后 gen_proto.py 才能正确生成）
- Task 3 无依赖，可与 Task 1、2 并行
- Task 4 无依赖，可与 Task 1-3 并行
- Task 5 无依赖，可与 Task 1-4 并行
- Task 6 依赖 Task 1-5 全部完成