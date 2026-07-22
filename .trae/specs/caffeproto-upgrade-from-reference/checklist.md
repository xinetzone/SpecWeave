# Checklist

- [ ] `gen_proto.py` 存在于 `external/chaos/caffe/` 目录
- [ ] `gen_proto.py` 运行成功，caffe_pb2.py 生成到 `python/` 和 `python/protos/`
- [ ] `protos/caffe.proto` 包含 NormalizeParameter 消息定义（across_spatial、scale_filler、channel_shared、eps 字段）
- [ ] `protos/caffe.proto` 包含 `norm_param` 字段（LayerParameter 中，ID 149）
- [ ] `python/utils.py` 包含 Conv2D、ConvTranspose2D、L2Norm 三个类
- [ ] `python/caffe_utils.py` 包含 unity_struct、unity_inputs、convert_num_to_name 三个函数
- [ ] `python/caffe_fuse.py` 包含 fuse_network 函数
- [ ] `python/test_l2norm.py` 存在且可运行
- [ ] `python/protos/caffe_pb2.py` 存在，与 `python/caffe_pb2.py` 内容一致
- [ ] `README.md` 包含 gen_proto.py 快速生成方式
- [ ] `README.md` 包含"添加新算子（四步法）"章节
- [ ] `README.md` 中 Python 版本为 3.14
- [ ] `CMakeLists.txt` 使用 `protobuf_generate_python` 而非自定义函数
- [ ] `python test_l2norm.py` 运行后 protobuf 相关测试全部 PASS
- [ ] `python -c "from python.caffe_pb2 import NormalizeParameter; print('OK')"` 成功执行
- [ ] 核心文件结构与 reference 对齐（gen_proto.py + python/ 下 6 个文件均存在）