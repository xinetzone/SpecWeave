# Checklist

- [x] `gen_proto.py` 存在于 `external/chaos/caffe/` 目录
- [x] `gen_proto.py` 运行成功，caffe_pb2.py 生成到 `python/` 和 `python/protos/`
- [x] `protos/caffe.proto` 包含 NormalizeParameter 消息定义（across_spatial、scale_filler、channel_shared、eps 字段）
- [x] `protos/caffe.proto` 包含 `norm_param` 字段（LayerParameter 中，ID 149）
- [x] `python/utils.py` 包含 Conv2D、ConvTranspose2D、L2Norm 三个类
- [x] `python/caffe_utils.py` 包含 unity_struct、unity_inputs、convert_num_to_name 三个函数
- [x] `python/caffe_fuse.py` 包含 fuse_network 函数
- [x] `python/test_l2norm.py` 存在且可运行
- [x] `python/protos/caffe_pb2.py` 存在，与 `python/caffe_pb2.py` 内容一致
- [x] `README.md` 包含 gen_proto.py 快速生成方式
- [x] `README.md` 包含"添加新算子（四步法）"章节
- [x] `README.md` 中 Python 版本为 3.14
- [x] `CMakeLists.txt` 使用 `protobuf_generate_python` 而非自定义函数
- [x] `python test_l2norm.py` 运行后 protobuf 相关测试全部 PASS
- [x] `python -c "from python.caffe_pb2 import NormalizeParameter; print('OK')"` 成功执行
- [x] 核心文件结构与 reference 对齐（gen_proto.py + python/ 下 6 个文件均存在）