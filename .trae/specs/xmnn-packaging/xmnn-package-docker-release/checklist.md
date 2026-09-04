# xmnn-package v1.0.0 Docker 镜像发布 - Verification Checklist

## 前置验证
- [ ] xmnn-runtime:latest 镜像存在于 WSL2 Docker 中
- [ ] 镜像 IMAGE_ID 已记录
- [ ] `/opt/verify-runtime.sh` 10 项自检全部 PASS
- [ ] WSL2 中 /mnt/d 可用磁盘空间 > 10GB
- [ ] package.sh 脚本可执行且无语法错误

## 打包执行
- [ ] `bash bin/package.sh --version v1.0.0 --archive` 退出码为 0
- [ ] 输出包含 "Docker image exported" 成功信息
- [ ] 输出包含 "version.json created" 成功信息
- [ ] 输出包含 "Package structure valid" 成功信息
- [ ] 输出包含 "Archive created" 成功信息

## 产物静态检查
- [ ] docker/xmnn-runtime-v1.0.0.tar 存在且大小 > 1GB
- [ ] version.json 是合法 JSON
- [ ] version.json 中 version 字段为 "v1.0.0"
- [ ] version.json 中 docker_tar 字段为 "xmnn-runtime-v1.0.0.tar"
- [ ] version.json 中 docker_image_id 不为 "unknown"（应为真实镜像 ID）
- [ ] xmnn-package-v1.0.0.tar.gz 存在且大小 > 500MB
- [ ] README.md 存在
- [ ] bin/docker-setup.sh 存在
- [ ] bin/lib/common.sh 存在
- [ ] examples/hello-world.py 存在
- [ ] docs/QUICKSTART.md 存在
- [ ] docs/DOCKER.md 存在
- [ ] docs/WSL2.md 存在
- [ ] tar 文件 sha256 校验和已计算并记录

## 镜像加载与运行时验证
- [ ] 旧 xmnn-runtime:latest 已删除（模拟新用户环境）
- [ ] `docker load -i docker/xmnn-runtime-v1.0.0.tar` 成功加载
- [ ] 加载后镜像标签为 xmnn-runtime:latest
- [ ] 重新运行 `/opt/verify-runtime.sh` 10/10 PASS
- [ ] `python -c "import tvm; import vta; import xmnn; print('XMNN OK')"` 输出 "XMNN OK"

## 用户流程验证
- [ ] `bash bin/docker-setup.sh --list` 正确列出镜像
- [ ] `bash bin/docker-setup.sh` 能检测到已加载镜像（幂等性）
- [ ] Hello World 示例运行成功（挂载 examples/ 目录）
- [ ] 无 ModuleNotFoundError 或 ImportError

## Windows 可访问性
- [ ] Windows 资源管理器中 tar 文件可见
- [ ] Windows 资源管理器中 tar.gz 文件可见
- [ ] tar.gz 归档内容完整（含 docker/、bin/、docs/、examples/、version.json、README.md）

## 交付物确认
- [ ] 交付物清单已汇总（文件列表 + 大小 + sha256）
- [ ] 交付方式已明确（目录拷贝 或 tar.gz）
- [ ] 用户快速开始命令已验证可用
