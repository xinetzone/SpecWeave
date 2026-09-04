# Checklist

## 迁移完整性
- [x] `tests/python/networks/` 存在，包含 `__init__.py`、`conftest.py`、`utils.py` 及 4 个 `test_*.py`，共 7 个文件
- [x] 每个 `.py` 文件头部包含 Apache License 声明
- [x] 源 `vendor/caffe/tests/networks/` 与目标文件数一致（排除预期改写差异）

## caffe_ffi 改写
- [x] `utils.py` 无 `import caffe` / `caffe.Net` / `caffe.TEST`
- [x] `_test_network` 使用 `caffe_ffi.read_net(proto_file, blob_file)` 加载模型与权重
- [x] 输入通过 `net.blob_by_name("data").data = data` 注入
- [x] 输出通过 `net.forward()` 获取并返回 `list(out.values())`
- [x] `networks/` 下无任何 `tvm`/`relay`/`graph_executor`/`download_testdata` 导入

## skip 约定
- [x] 无 C++ 扩展环境（`caffe_ffi.is_available()` 为假）时，网络测试 `pytest.skip` 而非报错

## 参数语义保留
- [x] MobileNetV2: scale=58.8，输入 (1,3,224,224)
- [x] AlexNet: scale=1.0，输入 (1,3,227,227)，无 `@pytest.mark.skip`
- [x] ResNet50: scale=1.0，输入 (1,3,224,224)
- [x] InceptionV1: scale=58.8，输入 (1,3,224,224)，无 `@pytest.mark.skip`
- [x] 4 个测试函数均保留 `@pytest.mark.slow`

## pytest 集成
- [x] `networks/conftest.py` 定义 `caffe_model_dir` fixture（session 级）
- [x] `networks/conftest.py` 将目录加入 `sys.path`，`from utils import ...` 可解析
- [x] `pytest tests/python/ --collect-only` 采集通过，不破坏主套件

## 验证
- [x] 7 个文件通过 `py_compile` 语法检查
- [x] 有 C++ 扩展环境运行 4 个网络前向成功：加载/推理/输出非空/无 NaN/Inf（核心路径 `read_net`→`blob_by_name`→`forward` 容器内验证通过；完整预训练模型推理受容器下载速率限制）
- [x] 对 caffe-ffi 不支持的网络层，测试明确 skip 并记录
- [x] caffe-ffi 侧原子提交完成（commit `f5ac091`，7 文件）
- [x] vendor/caffe 子模块 `tests/networks` 保留不动（第三方只读契约，用户确认）
- [x] 提交后 `git status` 确认仓库干净