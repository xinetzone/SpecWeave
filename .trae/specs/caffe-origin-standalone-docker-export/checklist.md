---
version: 1.0
date: 2026-07-27
---

# Caffe Origin 独立 Docker 镜像构建与分发 - Verification Checklist

## 构建脚本与镜像标签
- [ ] build.sh 支持构建 origin-runtime 镜像作为默认目标
- [ ] build.sh 支持 `--jupyter` 参数构建 origin-jupyter 镜像
- [ ] build.sh 支持 `--all` 参数一次性构建两个镜像
- [ ] build.sh 帮助信息完整准确
- [ ] 镜像标签命名清晰（origin-runtime, origin-jupyter）

## 镜像验证脚本
- [ ] verify-caffe.sh 已增强，包含 Python 版本检查
- [ ] verify-caffe.sh 验证 numpy/scipy/protobuf 导入
- [ ] verify-caffe.sh 验证 `import caffe` 成功
- [ ] verify-caffe.sh 验证 libcaffe.so 动态库可加载
- [ ] verify-caffe.sh 包含简单 Blob 创建/前向计算测试
- [ ] verify-caffe.sh 输出带颜色的 PASS/FAIL 结果
- [ ] verify-caffe.sh 返回正确的退出码（0=全部通过，非0=有失败）
- [ ] verify-caffe.sh 在容器内 PATH 中可直接调用
- [ ] `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 全部通过

## 独立运行脚本
- [ ] run-standalone.sh 已创建
- [ ] run-standalone.sh runtime 模式启动交互式 bash（无挂载）
- [ ] run-standalone.sh runtime 支持一次性命令执行（-- 后接命令）
- [ ] run-standalone.sh jupyter 模式自动映射端口 8888:8888 和 2222:22
- [ ] run-standalone.sh jupyter 模式支持环境变量传递密码/Token
- [ ] run-standalone.sh 启动后清晰显示访问 URL 和凭证
- [ ] run-standalone.sh 运行的容器不包含任何 -v 挂载参数
- [ ] run-standalone.sh 检测 Docker 未运行时给出友好提示

## 镜像导出脚本
- [ ] export.sh 已创建
- [ ] export.sh 默认导出两个镜像到 dist/ 目录
- [ ] dist/ 目录存在（含 .gitkeep）
- [ ] 导出文件名格式正确：caffe-cpu-origin-runtime_{YYYYMMDD}.tar
- [ ] 导出文件名格式正确：caffe-cpu-origin-jupyter_{YYYYMMDD}.tar
- [ ] export.sh 支持指定输出目录参数
- [ ] export.sh 支持只导出单个镜像参数
- [ ] export.sh 支持 --compress 参数生成 .tar.gz
- [ ] 导出后自动验证文件存在且大小合理
- [ ] 导出完成后打印 SHA256 校验和
- [ ] 导出的 tar 文件包含 manifest.json（OCI 格式正确）

## 镜像加载验证脚本
- [ ] load-and-verify.sh 已创建
- [ ] load-and-verify.sh 支持从 .tar 文件加载
- [ ] load-and-verify.sh 支持从 .tar.gz 压缩包加载
- [ ] 加载后自动运行 verify-caffe.sh 验证
- [ ] 加载验证成功后打印快速开始指引
- [ ] 处理加载错误（文件不存在、Docker 未运行、文件损坏）
- [ ] 删除本地镜像后，load-and-verify.sh 可从零成功加载

## 健康检查
- [ ] runtime 镜像 Dockerfile 包含 HEALTHCHECK 指令
- [ ] runtime 健康检查验证 caffe 可导入
- [ ] jupyter 镜像 HEALTHCHECK 检查 SSH 和 Jupyter 端口
- [ ] 健康检查参数配置合理（interval=30s, timeout=10s, start-period=10s, retries=3）
- [ ] 容器运行 30 秒后 docker inspect 显示 health: healthy

## 自包含性验证（核心验收）
- [ ] 不挂载任何宿主机目录时，`docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe"` 成功
- [ ] 不挂载目录时，`docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe; print(caffe.__version__)"` 输出版本号
- [ ] Jupyter 容器不挂载目录启动后，`docker exec` 进入容器可 import caffe
- [ ] Jupyter 容器内 Notebook 中可 import caffe
- [ ] 容器内所有依赖库均在镜像内，无运行时网络依赖

## 导出-加载闭环验证
- [ ] 两个镜像均成功导出到 dist/ 目录
- [ ] runtime tar 文件大小 > 1GB
- [ ] jupyter tar 文件大小 > 1.5GB
- [ ] docker rmi 删除本地镜像后，tar 文件可成功 docker load
- [ ] 加载后的镜像标签正确
- [ ] 加载后的镜像运行 verify-caffe.sh 全部通过
- [ ] 加载后的镜像与构建前功能一致

## 用户使用文档
- [ ] USER_GUIDE.md 已创建在 docker/origin/ 目录
- [ ] 包含简介章节说明镜像内容和用途
- [ ] 包含前置要求章节（Docker 安装说明/链接）
- [ ] 快速开始章节 ≤ 3 步即可运行第一个 Caffe 命令
- [ ] 基础镜像使用说明（交互式、运行脚本、常用命令）
- [ ] Jupyter 镜像使用说明（启动、访问 URL、Token/密码配置、SSH 登录）
- [ ] 包含验证镜像章节（运行验证脚本、预期输出说明）
- [ ] 包含文件传输方法（docker cp 示例，不使用"挂载"术语）
- [ ] FAQ 章节包含 ≥ 8 个常见问题及解决方案
- [ ] FAQ 覆盖：端口冲突、内存不足、加载失败、权限问题、Token 找不到、import 失败、容器退出、磁盘空间
- [ ] 包含卸载镜像说明
- [ ] 所有命令示例可直接复制粘贴执行
- [ ] 文档语言通俗易懂，避免内部开发术语
- [ ] Jupyter 访问说明包含完整 URL 示例和 Token 位置说明

## README 更新
- [ ] 现有 README.md 新增"镜像分发"章节
- [ ] 说明如何构建独立可分发镜像
- [ ] 说明如何导出镜像分发给用户
- [ ] 明确区分开发者模式（run.sh 挂载宿主机）和用户模式（run-standalone.sh 自包含）
- [ ] 添加 USER_GUIDE.md 的正确链接
- [ ] 原有开发者文档内容保持不变

## 跨环境兼容性
- [ ] 镜像标签符合 OCI 标准
- [ ] 镜像不依赖特定 CPU 指令集（可在多数 x86_64 机器运行）
- [ ] 使用标准 docker save/load 格式，无特殊编码
- [ ] 文档说明支持的 Docker 版本要求（20.10+）
- [ ] 文件路径使用 Linux 风格（容器内），Windows/macOS 路径转换说明在 FAQ 中

## 交付物清单
- [ ] build.sh（更新后）
- [ ] scripts/verify-caffe.sh（增强后）
- [ ] run-standalone.sh（新建）
- [ ] export.sh（新建）
- [ ] load-and-verify.sh（新建）
- [ ] Dockerfile（添加 HEALTHCHECK）
- [ ] Dockerfile.jupyter-ssh（添加 HEALTHCHECK，如需单独修改）
- [ ] dist/ 目录（含 .gitkeep）
- [ ] USER_GUIDE.md（新建）
- [ ] README.md（更新分发章节）
- [ ] 两个导出的 tar 文件（在 dist/ 中）
