---
version: 1.1
date: 2026-07-27
note: 代码和文档已就绪。标记 [x] 为已完成（静态验证通过），标记 [ ] 的项需要在装有 Docker 的机器上执行实际构建和运行验证（见 tasks.md Task 8/9 执行步骤）
---

# Caffe Origin 独立 Docker 镜像构建与分发 - Verification Checklist

## 构建脚本与镜像标签
- [x] build.sh 支持构建 origin-runtime 镜像作为默认目标
- [x] build.sh 支持 `--jupyter` 参数构建 origin-jupyter 镜像
- [x] build.sh 支持 `--all` 参数一次性构建两个镜像
- [x] build.sh 帮助信息完整准确
- [x] 镜像标签命名清晰（origin-runtime, origin-jupyter）
- [ ] build.sh --all 实际构建两个镜像成功（需 Docker）

## 镜像验证脚本
- [x] verify-caffe.sh 已增强，包含 Python 版本检查
- [x] verify-caffe.sh 验证 numpy/scipy/protobuf 导入（protobuf 强制 3.x）
- [x] verify-caffe.sh 验证 `import caffe` 成功
- [x] verify-caffe.sh 验证 libcaffe.so 动态库存在
- [x] verify-caffe.sh 包含 Blob 创建和数据读写测试
- [x] verify-caffe.sh 输出带颜色的 PASS/FAIL 结果
- [x] verify-caffe.sh 返回正确的退出码（0=全部通过，非0=有失败）
- [x] verify-caffe.sh 被 COPY 到容器内 /usr/local/bin/（PATH 中可直接调用）
- [x] bash -n 语法检查通过
- [ ] `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 全部通过（需 Docker）

## 独立运行脚本
- [x] run-standalone.sh 已创建
- [x] run-standalone.sh runtime 模式启动交互式 bash（无挂载）
- [x] run-standalone.sh runtime 支持一次性命令执行（-- 后接命令）
- [x] run-standalone.sh jupyter 模式自动映射端口 127.0.0.1:8888:8888 和 127.0.0.1:2222:22
- [x] run-standalone.sh jupyter 模式支持环境变量传递密码/Token
- [x] run-standalone.sh 启动后清晰显示访问 URL 和凭证
- [x] run-standalone.sh 运行的容器不包含任何 -v 挂载参数（代码确认）
- [x] run-standalone.sh 检测 Docker 未运行/镜像不存在时给出友好提示
- [x] bash -n 语法检查通过
- [ ] run-standalone.sh runtime -- python3 -c "import caffe" 实际执行成功（需 Docker）
- [ ] run-standalone.sh jupyter 启动后端口可访问（需 Docker）

## 镜像导出脚本
- [x] export.sh 已创建
- [x] export.sh 默认导出两个镜像到 dist/ 目录
- [x] dist/ 目录存在（含 .gitkeep）
- [x] 导出文件名格式正确：caffe-cpu-origin-runtime_{YYYYMMDD}.tar
- [x] 导出文件名格式正确：caffe-cpu-origin-jupyter_{YYYYMMDD}.tar
- [x] export.sh 支持 -o/--output 指定输出目录参数
- [x] export.sh 支持 --runtime 和 --jupyter 只导出单个镜像
- [x] export.sh 支持 --compress/-z 参数生成 .tar.gz
- [x] 导出后自动验证文件存在且大小>0
- [x] 导出完成后打印 SHA256 校验和
- [x] 包含磁盘空间检查（至少 8GB）
- [x] bash -n 语法检查通过
- [ ] 实际执行 export.sh 生成 tar 文件（需 Docker）
- [ ] 导出的 tar 文件包含 manifest.json（OCI 格式正确）（需 Docker）

## 镜像加载验证脚本
- [x] load-and-verify.sh 已创建
- [x] load-and-verify.sh 支持从 .tar 文件加载
- [x] load-and-verify.sh 支持从 .tar.gz 压缩包加载
- [x] 加载后自动运行 verify-caffe.sh 验证（使用 --entrypoint 绕过 jupyter entrypoint）
- [x] 加载验证成功后打印快速开始指引
- [x] 自动检测 dist/ 目录下最新镜像文件
- [x] 处理加载错误（文件不存在、Docker 未运行、文件损坏）
- [x] bash -n 语法检查通过
- [ ] 从零环境（docker rmi 后）实际加载并验证成功（需 Docker）

## 健康检查
- [x] runtime 镜像 Dockerfile 包含 HEALTHCHECK 指令
- [x] healthcheck-caffe.sh 已创建（验证 Python 和 caffe 导入）
- [x] runtime 健康检查验证 caffe 可导入
- [x] jupyter 镜像 HEALTHCHECK 检查 SSH 和 Jupyter 端口（已有）
- [x] 健康检查参数配置合理（interval=30s, timeout=10s, start-period=5s, retries=3）
- [x] healthcheck-caffe.sh bash -n 语法检查通过
- [ ] 容器运行后 docker inspect 显示 health: healthy（需 Docker）

## Dockerfile 修改
- [x] Dockerfile runtime 阶段 COPY verify-caffe.sh 和 healthcheck-caffe.sh 到 /usr/local/bin/
- [x] Dockerfile runtime 阶段设置可执行权限
- [x] Dockerfile runtime 阶段在 CMD 前添加 HEALTHCHECK 指令
- [x] 构建上下文路径正确（COPY 源路径相对于 caffe/ 根目录）
- [x] Dockerfile.jupyter-ssh 无需修改（已有独立 HEALTHCHECK 和 verify-caffe.sh COPY）

## 自包含性验证（核心验收）- 需 Docker
- [ ] 不挂载任何宿主机目录时，`docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe"` 成功
- [ ] 不挂载目录时，`docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe; print(caffe.__version__)"` 输出版本号
- [ ] Jupyter 容器不挂载目录启动后，`docker exec` 进入容器可 import caffe
- [ ] Jupyter 容器内 Notebook 中可 import caffe
- [ ] 容器内所有依赖库均在镜像内，无运行时网络依赖
- [ ] docker inspect 确认容器无 Mounts/Volumes（除了镜像内置 VOLUME）

## 导出-加载闭环验证 - 需 Docker
- [ ] 两个镜像均成功导出到 dist/ 目录
- [ ] runtime tar 文件大小 > 1GB
- [ ] jupyter tar 文件大小 > 1.5GB
- [ ] docker rmi 删除本地镜像后，tar 文件可成功 docker load
- [ ] 加载后的镜像标签正确
- [ ] 加载后的镜像运行 verify-caffe.sh 全部通过
- [ ] 加载后的镜像与构建前功能一致
- [ ] SHA256 校验和验证通过

## 用户使用文档
- [x] USER_GUIDE.md 已创建在 docker/origin/ 目录
- [x] 包含概述章节说明镜像内容和两个版本的区别
- [x] 包含分发包内容说明
- [x] 快速开始章节 3 步即可运行第一个 Caffe 命令
- [x] Runtime 镜像使用说明（交互式、一次性命令、验证、数据持久化）
- [x] Jupyter 镜像使用说明（启动、访问 URL、Token/密码配置、SSH 登录、停止）
- [x] 包含手动 Docker 命令（高级用户）
- [x] 包含验证镜像章节（验证脚本、健康状态检查、故障排查）
- [x] 包含 docker cp 文件传输方法
- [x] FAQ 章节包含 ≥ 8 个常见问题及解决方案（9 个问题）
- [x] FAQ 覆盖：镜像损坏、端口占用、文件持久化、Jupyter/SSH访问、docker cp、GPU说明、密码/Token修改、Python包安装
- [x] 包含目录结构说明
- [x] 所有命令示例可直接复制粘贴执行
- [x] 文档语言通俗易懂，面向非开发者
- [x] Jupyter 访问说明包含完整 URL 示例和 Token 位置说明

## README 更新
- [x] 现有 README.md 新增"独立镜像分发"章节
- [x] 说明如何构建独立可分发镜像（build.sh --all → export.sh）
- [x] 说明如何导出镜像分发给用户
- [x] 明确区分开发者模式（run.sh 挂载宿主机）和用户模式（run-standalone.sh 自包含）
- [x] 添加 USER_GUIDE.md 的正确链接
- [x] 更新了目录结构（新文件列表）
- [x] 更新了构建产物标签名（origin-runtime/origin-jupyter）
- [x] 更新了健康检查列（runtime 镜像也有健康检查）
- [x] 同步更新了文档中旧标签引用
- [x] 原有开发者文档内容保持不变

## 跨环境兼容性
- [x] 镜像标签符合 OCI 标准（标准 docker save/load 格式）
- [x] 使用标准 docker save/load 格式，无特殊编码
- [x] .gitattributes 配置 `*.sh text eol=lf` 确保脚本 LF 行尾
- [x] .dockerignore 排除 dist/、*.tar、*.tar.gz 防止构建上下文膨胀
- [x] 端口绑定到 127.0.0.1（安全考虑）
- [ ] 实际在 Windows/macOS/Linux 不同平台加载运行验证（需多平台测试）

## 交付物清单
- [x] build.sh（更新后，支持 --jupyter/--all）
- [x] scripts/verify-caffe.sh（增强后，12项检查+颜色输出+退出码）
- [x] scripts/healthcheck-caffe.sh（新建，runtime健康检查）
- [x] run-standalone.sh（新建，自包含运行脚本）
- [x] export.sh（新建，导出脚本+SHA256+压缩）
- [x] load-and-verify.sh（新建，加载+验证一体化）
- [x] Dockerfile（添加 HEALTHCHECK 和脚本 COPY）
- [x] Dockerfile.jupyter-ssh（已有HEALTHCHECK，无需修改）
- [x] dist/ 目录（含 .gitkeep）
- [x] USER_GUIDE.md（新建，面向非开发者）
- [x] README.md（更新分发章节）
- [ ] 两个导出的 tar 文件（在 dist/ 中，需 Docker 构建后执行 export.sh）
