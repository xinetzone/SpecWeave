# xmnn-package v1.0.0 Docker 镜像发布 - The Implementation Plan

## [x] Task 1: 前置验证（确认待发布镜像状态）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 WSL2 中确认 xmnn-runtime:latest 镜像存在
  - 记录镜像 IMAGE_ID、创建时间、虚拟大小
  - 运行镜像自检 `/opt/verify-runtime.sh` 确认 10/10 PASS
  - 检查磁盘剩余空间（确保有 >10GB 可用空间）
  - 确认 package.sh 脚本可执行
- **Acceptance Criteria Addressed**: AC-1（前置条件验证）
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker image inspect xmnn-runtime:latest` 返回有效 JSON，记录 Id 字段 ✅ ID: sha256:4e5ad5175782fdca3c7ecaafe93723532b7cafdcfe47686a831b8a50edc1c52e
  - `programmatic` TR-1.2: `docker run --rm xmnn-runtime:latest /opt/verify-runtime.sh` 输出 "SUMMARY: 10 passed, 0 failed" ✅
  - `programmatic` TR-1.3: `df -h /mnt/d` 显示可用空间 >10GB ✅ 198GB available
- **Notes**: 镜像大小 4.33GB，创建于 2026-08-10，10项自检全部PASS

## [ ] Task 2: 执行 package.sh 打包
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在 WSL2 中进入包目录：`cd /mnt/d/spaces/SpecWeave/external/chaos/ai/xmnn-package`
  - 执行打包命令：`bash bin/package.sh --version v1.0.0 --archive`
  - 记录打包过程输出（日志）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本退出码为 0，最后输出 "Package Build Complete"
  - `programmatic` TR-2.2: 脚本输出包含 "Docker image exported"、"version.json created"、"Package structure valid"、"Archive created"
- **Notes**: docker save 过程可能需要 2-5 分钟（取决于磁盘速度）

## [ ] Task 3: 产物静态验证
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 验证 docker/xmnn-runtime-v1.0.0.tar 存在且大小 >1GB
  - 验证 version.json 是合法 JSON，字段完整
  - 验证 xmnn-package-v1.0.0.tar.gz 存在且大小 >500MB
  - 验证包结构完整性（9个必要文件/目录检查）
  - 生成 tar 文件的 sha256 校验和
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: `ls -la docker/xmnn-runtime-v1.0.0.tar` 显示文件大小 >1GB
  - `programmatic` TR-3.2: `python3 -c "import json; json.load(open('version.json'))"` 无异常退出
  - `programmatic` TR-3.3: `ls -la xmnn-package-v1.0.0.tar.gz` 显示文件大小 >500MB
  - `programmatic` TR-3.4: 检查 README.md、bin/docker-setup.sh、bin/lib/common.sh、examples/hello-world.py、docs/QUICKSTART.md、docs/DOCKER.md、docs/WSL2.md、version.json、docker/xmnn-runtime-v1.0.0.tar 全部存在
  - `programmatic` TR-3.5: `sha256sum docker/xmnn-runtime-v1.0.0.tar` 输出 64 位十六进制哈希
- **Notes**: version.json 中 docker_image_id 如果是 "unknown" 是因为 package.sh 在 --from-image-tar 模式下无法获取，但本次使用默认 docker save 模式应能获取到实际 ID

## [ ] Task 4: 镜像加载与运行时验证
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 删除本地已有 xmnn-runtime:latest 镜像（模拟全新用户环境）：`docker rmi xmnn-runtime:latest`
  - 从导出的 tar 加载镜像：`docker load -i docker/xmnn-runtime-v1.0.0.tar`
  - 运行 10 项自检确认全部 PASS
  - 运行快速导入测试：`docker run --rm xmnn-runtime:latest python -c "import tvm; import vta; import xmnn; print('XMNN OK')"`
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: `docker rmi xmnn-runtime:latest` 成功（允许忽略"镜像被容器引用"错误，如有必要先停止相关容器）
  - `programmatic` TR-4.2: `docker load -i docker/xmnn-runtime-v1.0.0.tar` 输出 "Loaded image: xmnn-runtime:latest"
  - `programmatic` TR-4.3: `docker run --rm xmnn-runtime:latest /opt/verify-runtime.sh` 输出 "SUMMARY: 10 passed, 0 failed"
  - `programmatic` TR-4.4: 快速导入测试输出 "XMNN OK"，无 Traceback
- **Notes**: 删除旧镜像前需确保 chaos-ai-dev 容器不依赖 xmnn-runtime（dev 容器使用的是 chaos-ai-npu 镜像，不是 runtime）

## [ ] Task 5: 用户流程走查（docker-setup.sh + Hello World）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 模拟全新用户：在一个干净的 shell 中执行 `bash bin/docker-setup.sh`
  - 验证脚本自动检测 docker/ 下的 tar 文件、加载镜像、运行自检
  - 运行 Hello World 示例：挂载 examples/ 目录执行 hello-world.py
  - 验证 --list 参数可用
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: `bash bin/docker-setup.sh --list` 列出 xmnn-runtime-v1.0.0.tar
  - `programmatic` TR-5.2: `bash bin/docker-setup.sh --no-verify` 成功加载镜像（因为上一步已加载，预期提示 already exists）
  - `programmatic` TR-5.3: `docker run --rm -v $(pwd)/examples:/workspace/examples xmnn-runtime:latest python /workspace/examples/hello-world.py` 无报错输出
- **Notes**: docker-setup.sh 重复加载是幂等的（会覆盖标签），无需再次删除镜像

## [ ] Task 6: Windows 路径验证与交付确认
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 在 Windows 侧验证 tar 文件和 tar.gz 文件可见
  - 验证 tar.gz 可解压（列出内容）
  - 汇总发布产物清单和校验信息
  - 给出交付说明
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: Windows 侧 `Test-Path "d:\spaces\SpecWeave\external\chaos\ai\xmnn-package\docker\xmnn-runtime-v1.0.0.tar"` 返回 True
  - `programmatic` TR-6.2: Windows 侧 `Test-Path "d:\spaces\SpecWeave\external\chaos\ai\xmnn-package\xmnn-package-v1.0.0.tar.gz"` 返回 True
  - `programmatic` TR-6.3: `tar -tzf xmnn-package-v1.0.0.tar.gz | head -20` 列出合理的目录结构
- **Notes**: 交付物为整个 xmnn-package 目录（包含 docker/ 下的 tar）或 tar.gz 归档
