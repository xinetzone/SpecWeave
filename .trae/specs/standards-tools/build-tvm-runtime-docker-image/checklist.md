# 构建 TVM/VTA 纯净运行时 Docker 镜像 - Verification Checklist

## Dockerfile 验证
- [ ] Dockerfile.runtime_wheels 文件已创建在 docker/local/conda/ 目录下
- [ ] Dockerfile 基于 continuumio/miniconda3:latest 基础镜像
- [ ] 支持 PYTHON_VERSION build-arg（默认 3.14）
- [ ] 支持 TVM_VERSION build-arg（默认 0.19.0）
- [ ] 创建独立的 tvm-runtime Conda 环境
- [ ] 从 docker/local/nuitka/*/dist/ 复制 wheel 包到镜像中
- [ ] 使用 pip 安装 wheel 包（tvm 先于 vta）
- [ ] 安装 numpy, ml_dtypes, typing_extensions 依赖
- [ ] test_wheel.py 被复制到镜像中的 /opt/ 目录
- [ ] 构建时执行验证命令（python 版本、tvm/vta 导入）
- [ ] 清理 apt 缓存（rm -rf /var/lib/apt/lists/*）
- [ ] 清理 conda 缓存（conda clean -a -y）
- [ ] 清理 pip 缓存（pip cache purge）
- [ ] 清理临时文件（rm -rf /tmp/*）
- [ ] LD_LIBRARY_PATH 配置正确，包含 tvm/_libs 目录
- [ ] Conda 环境自动激活（bashrc 配置或 ENV 设置）
- [ ] 默认工作目录为 /workspace

## 构建脚本验证
- [ ] build_runtime_image.sh 文件已创建在 docker/local/conda/ 目录下
- [ ] 脚本具有可执行权限
- [ ] 支持 --python-version 参数
- [ ] 支持 --tvm-version 参数
- [ ] 支持 --tag 参数自定义镜像标签
- [ ] 支持 --help 输出使用说明
- [ ] 脚本执行前检查 wheel 包是否存在
- [ ] 使用正确的 docker build 上下文（npu_tvm 根目录）
- [ ] 构建完成后打印镜像信息（大小、标签、ID）
- [ ] 默认镜像标签格式为 tvm-runtime:<version>-py<python_version>

## 导出脚本验证
- [ ] export_runtime_image.sh 文件已创建在 docker/local/conda/ 目录下
- [ ] 脚本具有可执行权限
- [ ] 支持 --tag 参数指定镜像
- [ ] 支持 --output 参数指定输出路径
- [ ] 支持 --compress 参数启用 gzip 压缩
- [ ] 默认输出到 docker/local/dist/ 目录
- [ ] 导出完成后打印文件路径和大小
- [ ] 打印 docker load 导入命令提示

## 镜像功能验证
- [ ] docker build 成功完成，无错误退出
- [ ] 镜像大小 < 1 GB
- [ ] docker run 启动容器无报错
- [ ] 容器内 python --version 输出正确版本（3.14.x）
- [ ] 容器内 conda 环境默认激活为 tvm-runtime
- [ ] 容器内 import tvm 成功，版本号为 0.19.0
- [ ] 容器内 import vta 成功
- [ ] 容器内运行 python /opt/test_wheel.py 输出 "All tests passed"
- [ ] TVM 张量创建功能正常（tvm.nd.array）
- [ ] TVM 数组计算功能正常
- [ ] TVM TE 计算功能正常
- [ ] TVM Relay 模块可用
- [ ] TVM LLVM target 可用
- [ ] VTA 环境加载正常（vta.get_env()）
- [ ] 未设置 PYTHONPATH 环境变量（干净环境）
- [ ] libtvm.so 和 libtvm_runtime.so 可被正确加载（无动态链接错误）

## 镜像导出/导入验证
- [ ] docker save 成功导出 tar 文件
- [ ] tar 文件大小合理（与镜像大小相当）
- [ ] gzip 压缩后文件明显减小（如启用 --compress）
- [ ] docker load -i 可成功导入 tar 文件
- [ ] 导入后的镜像可正常启动容器
- [ ] 导入后的镜像中 tvm/vta 可正常导入

## 文档验证
- [ ] RUNTIME_IMAGE_USAGE.md 文件已创建在 docker/local/conda/ 目录下
- [ ] 文档包含镜像简介章节
- [ ] 文档包含构建镜像的命令说明
- [ ] 文档包含导出/导入镜像的命令说明
- [ ] 文档包含启动容器的命令示例
- [ ] 文档包含验证安装的步骤说明
- [ ] 文档包含基本用法代码示例
- [ ] 文档包含环境变量说明
- [ ] 文档包含故障排查章节
- [ ] 文档中的所有命令均可直接复制执行
- [ ] 文档使用中文编写，表述清晰
