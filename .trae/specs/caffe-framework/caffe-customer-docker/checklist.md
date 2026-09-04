# Caffe 客户分发 Docker 镜像 - Verification Checklist

## 目录结构与文件完整性
- [ ] pycaffe-customer/ 目录已创建在正确路径下
- [ ] Dockerfile 存在且语法正确
- [ ] .dockerignore 存在且包含必要排除规则（caffex/、.git、__pycache__、*.pyc 等）
- [ ] config/ 目录包含所有必要配置文件（supervisord.conf、sshd_config、jupyter_notebook_config.py、supervisor/conf.d/）
- [ ] scripts/ 目录包含 healthcheck.sh
- [ ] entrypoint.sh 存在且可执行
- [ ] caffe-verify 脚本存在（在 scripts/ 或 Dockerfile 中创建到 /usr/local/bin/）
- [ ] build.sh 构建脚本存在且可执行
- [ ] export.sh 导出脚本存在且可执行
- [ ] examples/resnet50/ 目录包含 ResNet50 示例文件（prototxt、caffemodel、demo.png、config.toml、infer.py）
- [ ] README.md 客户文档存在且内容完整

## Dockerfile 质量检查
- [ ] 使用 FROM ubuntu:26.04（固定版本，非 latest）
- [ ] 不依赖任何本地预构建镜像（无 FROM caffe-cpu:standalone-pycaffe）
- [ ] 多阶段构建（base-system → base-builder → caffe-builder → customer-runtime-setup → customer-runtime）
- [ ] 最终 runtime 阶段不包含构建工具（gcc/g++/cmake/ninja/git/build-essential）
- [ ] 默认 locale 为 C.UTF-8（非 zh_CN.UTF-8）
- [ ] 默认时区为 UTC，支持 TZ 环境变量配置
- [ ] 使用官方 Ubuntu apt 源（默认），支持 build-arg 替换镜像源
- [ ] pip 包使用固定版本（==）
- [ ] 构建时执行 apt-get upgrade 安装安全更新
- [ ] 每个 RUN 指令后清理 apt 缓存和临时文件
- [ ] pip 安装使用 --no-cache-dir
- [ ] 包含完整 LABEL 元数据（maintainer、version、description、source）
- [ ] 每个构建阶段有清晰注释说明用途
- [ ] 标注所有关键软件版本
- [ ] 构建信息写入 /etc/caffe-customer-release
- [ ] PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python 环境变量已设置
- [ ] HEALTHCHECK 配置同时检测 SSH 和 Jupyter
- [ ] ENTRYPOINT 使用 tini 作为 PID 1
- [ ] CMD 启动 supervisord
- [ ] 不包含任何 SSH 私钥或密钥材料（仅在 entrypoint 启动时生成 host keys）
- [ ] WORKDIR 设置为 /workspace
- [ ] EXPOSE 22 8888
- [ ] VOLUME ["/workspace"]
- [ ] 零 caffex/ 依赖（无 COPY caffex/、无引用 caffex 路径）

## 构建与镜像验证
- [ ] docker build 成功完成无错误
- [ ] 镜像体积 < 3GB（目标 < 2.5GB）
- [ ] docker inspect 显示 LABEL 元数据完整
- [ ] 镜像中不存在 /var/lib/apt/lists/ 内容（apt 缓存已清理）
- [ ] 镜像中不存在构建工具（验证 which gcc cmake ninja git 均返回空）
- [ ] 镜像中不存在 .git 目录
- [ ] builder 用户存在且 UID=1000
- [ ] ResNet50 示例文件存在于镜像内 /opt/caffe-examples/resnet50/

## 容器运行验证
- [ ] docker run 成功启动容器
- [ ] 容器在 10 秒内进入 healthy 状态
- [ ] docker ps 显示容器状态为 Up 且 healthy
- [ ] docker logs 显示清晰的欢迎 banner
- [ ] banner 包含 Jupyter URL（http://localhost:8888/）
- [ ] banner 包含 Jupyter token（caffe-token，或环境变量设置的值）
- [ ] banner 包含 SSH 连接信息（ssh builder@host -p port）
- [ ] banner 包含 SSH 默认密码（caffepass）和修改提示
- [ ] banner 包含 caffe-verify 自检命令提示
- [ ] banner 包含安全修改默认密码的警告
- [ ] Jupyter 进程以 builder 用户运行（非 root）
- [ ] SSH 进程以 root 运行（sshd 需要 root 绑定 22 端口，但认证后降级）
- [ ] SSH 配置禁止 root 登录

## 服务功能验证
- [ ] HTTP 访问 http://localhost:8888/ 返回 200/302（非连接拒绝）
- [ ] Jupyter 使用默认 token `caffe-token` 可成功登录
- [ ] Jupyter 中可创建新 notebook
- [ ] Jupyter notebook 中可执行 `import pycaffe`
- [ ] SSH 连接 localhost:2222 使用 builder/caffepass 可成功登录
- [ ] SSH 登录后可执行 python 命令

## PyCaffe 功能验证
- [ ] `python -c "import pycaffe"` 成功无报错
- [ ] `python -c "import pycaffe; print(pycaffe.__version__)"` 输出 1.0.0-slim
- [ ] pycaffe.Net 类可导入
- [ ] pycaffe.set_mode_cpu() 可执行
- [ ] LeNet 网络可创建并执行 forward（不抛异常）

## 自检命令验证
- [ ] caffe-verify 命令存在于 /usr/local/bin/
- [ ] caffe-verify 可执行
- [ ] caffe-verify 报告 pycaffe import PASS
- [ ] caffe-verify 报告版本检查 PASS
- [ ] caffe-verify 报告 Net 类可用 PASS
- [ ] caffe-verify 报告 LeNet forward PASS
- [ ] caffe-verify 报告 Jupyter 端口检查 PASS
- [ ] caffe-verify 报告 SSH 端口检查 PASS
- [ ] caffe-verify 报告 ResNet50 demo 推理 PASS
- [ ] caffe-verify 最终退出码为 0
- [ ] caffe-verify 输出格式清晰易读

## ResNet50 Demo 验证
- [ ] infer.py 可成功执行
- [ ] 推理输出分类结果（无错误）
- [ ] Jupyter 中可打开并运行示例 notebook（如有）

## 安全验证
- [ ] sshd_config 中 PermitRootLogin no
- [ ] 镜像中不存在预生成的 SSH host keys（/etc/ssh/ssh_host_* 不存在或由 entrypoint 重新生成）
- [ ] /etc/sudoers.d/ 中默认无 NOPASSWD 规则（或由 GRANT_SUDO 环境变量控制，默认为 no）
- [ ] 镜像中不包含任何硬编码密码/密钥/token（默认凭证在文档中标注，非硬编码敏感信息）
- [ ] pip list 显示所有包版本固定

## docker save/load 往返验证
- [ ] docker save 成功生成 tar 文件
- [ ] tar 文件大小合理（与镜像大小匹配）
- [ ] 在干净环境（无原有镜像）中 docker load -i 成功
- [ ] load 后镜像名和 tag 正确
- [ ] load 后容器可正常启动运行
- [ ] load 后 caffe-verify 所有检查项 PASS

## 文档质量验证
- [ ] README.md 包含 Quick Start 章节（3步快速开始）
- [ ] README.md 包含 docker load 命令示例
- [ ] README.md 包含 docker run 命令示例（含端口映射）
- [ ] README.md 明确标注默认凭证（用户名/密码/token）
- [ ] README.md 包含修改默认凭证的醒目安全警告
- [ ] README.md 包含 caffe-verify 自检方法
- [ ] README.md 包含 ResNet50 demo 运行方法
- [ ] README.md 列出所有可用环境变量
- [ ] README.md 包含安全最佳实践章节
- [ ] README.md 包含 Troubleshooting 常见问题章节
- [ ] README.md 包含版本和维护者信息
- [ ] 文档中所有命令示例可复制粘贴执行
- [ ] 非技术人员按 Quick Start 可独立完成镜像加载和运行

## 可维护性检查
- [ ] Dockerfile 每个阶段注释清晰说明用途
- [ ] 关键步骤有注释解释"为什么"而不仅是"做什么"
- [ ] 所有软件版本在 Dockerfile 中明确标注
- [ ] /etc/caffe-customer-release 包含构建日期、基础镜像、版本号等信息
- [ ] build.sh 有错误检查和清晰的错误提示
- [ ] export.sh 支持自定义输出文件名
- [ ] 脚本使用 set -euo pipefail 严格模式
