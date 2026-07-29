# Caffe Jupyter Docker镜像构建与导出 - Product Requirement Document

## Overview
- **Summary**: 使用指定的Dockerfile.jupyter-ssh构建caffe-cpu:jupyter多阶段Docker镜像，该镜像包含BVLC Caffe CPU版本、SSH服务、Jupyter Notebook/Lab环境，构建成功后将镜像导出为tar文件保存到D:\BaiduSyncdisk\docker目录。
- **Purpose**: 构建可复用的Caffe深度学习Jupyter开发环境镜像，并保存到本地备份路径以支持后续离线加载、分发和部署。
- **Target Users**: 深度学习开发者、需要使用Caffe框架进行模型训练和推理的研究人员。

## Goals
- 使用Dockerfile.jupyter-ssh的runtime-jupyter目标成功构建caffe-cpu:jupyter镜像
- 确保镜像内Caffe (PyCaffe) 可正常导入和使用
- 确保镜像内Jupyter Notebook/Lab和SSH服务配置正确
- 将构建完成的镜像保存为tar格式文件到D:\BaiduSyncdisk\docker
- 验证保存的镜像文件可正常加载和运行

## Non-Goals (Out of Scope)
- 修改Dockerfile或Caffe源码
- 构建GPU版本镜像
- 配置远程镜像仓库推送
- 修改容器运行时配置（端口映射、卷挂载等）
- 镜像体积优化（多阶段构建已包含在Dockerfile中）

## Background & Context
- Dockerfile位于：[Dockerfile.jupyter-ssh](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/docker/origin/Dockerfile.jupyter-ssh)
- 构建命令（Dockerfile第14行）：`docker build -t caffe-cpu:jupyter --target runtime-jupyter -f docker/origin/Dockerfile.jupyter-ssh .`
- 构建上下文需要在caffe根目录（包含caffex/源码目录）
- Docker环境运行在WSL Ubuntu-24.04中（Docker 29.6.1）
- 目标保存路径：D:\BaiduSyncdisk\docker（Windows路径，对应WSL中的/mnt/d/BaiduSyncdisk/docker）
- 之前已有成功构建和运行该镜像的历史记录（session 6a66097032cb82786350da5a）

## Functional Requirements
- **FR-1**: 执行docker build命令，使用指定Dockerfile和runtime-jupyter目标构建镜像
- **FR-2**: 构建过程无错误退出，最终镜像标记为caffe-cpu:jupyter
- **FR-3**: 镜像包含正确的Caffe编译产物（libcaffe.so、_caffe.so Python绑定）
- **FR-4**: 镜像内Python可正常import caffe，核心功能可用
- **FR-5**: 镜像包含Jupyter Notebook/Lab、SSH服务、supervisord管理
- **FR-6**: 使用docker save命令将镜像导出为tar文件
- **FR-7**: 导出的tar文件保存到D:\BaiduSyncdisk\docker目录
- **FR-8**: 导出文件完整性可验证（大小合理、可通过docker load加载）

## Non-Functional Requirements
- **NFR-1**: 构建过程可重复，相同输入产生相同功能的镜像
- **NFR-2**: 构建日志可追溯，关键步骤有输出
- **NFR-3**: 镜像保存后能成功加载并运行基础功能验证
- **NFR-4**: 保存文件命名规范（含镜像名和时间戳或版本标识）

## Constraints
- **Technical**: 
  - 必须使用WSL Ubuntu-24.04中的Docker环境
  - 构建上下文必须是caffe根目录（d:\spaces\SpecWeave\projects\xuanspace\vendor\caffe\）
  - Dockerfile中COPY caffex需要源码目录存在且完整
  - 国内网络环境下apt/pip源已配置为阿里云镜像（Dockerfile内已处理）
- **Business**: 
  - 镜像保存到指定的百度同步盘目录
- **Dependencies**: 
  - Docker daemon正常运行
  - caffex/源码目录完整（包含Makefile、源码、Python绑定）
  - docker/origin/config/和scripts/目录下配置文件完整
  - 磁盘空间充足（镜像预计1-3GB）

## Assumptions
- WSL Ubuntu-24.04中的Docker daemon已启动且可正常使用
- caffex目录已包含完整可编译的Caffe源码
- D:\BaiduSyncdisk\docker目录存在且有写入权限
- 网络连接正常（用于apt/pip下载依赖包）
- 之前构建过的镜像缓存可加速本次构建（如有）

## Acceptance Criteria

### AC-1: Docker镜像构建成功完成
- **Given**: Docker daemon运行正常，caffex源码完整
- **When**: 在caffe根目录执行指定的docker build命令
- **Then**: 命令退出码为0，本地镜像列表中存在caffe-cpu:jupyter
- **Verification**: `programmatic`
- **Notes**: 检查`docker images caffe-cpu:jupyter`有输出

### AC-2: Caffe在镜像内可正常导入
- **Given**: caffe-cpu:jupyter镜像已构建成功
- **When**: 运行临时容器执行`python -c "import caffe; print(caffe.__version__)"`
- **Then**: 命令成功执行，输出Caffe版本信息（1.0），无导入错误
- **Verification**: `programmatic`

### AC-3: 镜像内Jupyter环境可用
- **Given**: caffe-cpu:jupyter镜像已构建成功
- **When**: 运行临时容器执行`jupyter --version`
- **Then**: 命令成功执行，显示notebook、jupyterlab等组件版本
- **Verification**: `programmatic`

### AC-4: 镜像导出tar文件生成成功
- **Given**: caffe-cpu:jupyter镜像存在
- **When**: 执行docker save命令将镜像导出到D:\BaiduSyncdisk\docker
- **Then**: 指定路径下生成.tar文件，文件大小大于100MB
- **Verification**: `programmatic`

### AC-5: 导出的镜像文件可正常加载
- **Given**: 已导出的caffe-cpu-jupyter.tar文件存在
- **When**: 先删除本地镜像，再执行docker load加载tar文件
- **Then**: 加载成功，镜像列表中重新出现caffe-cpu:jupyter，且Caffe可正常导入
- **Verification**: `programmatic`

### AC-6: 加载后的镜像可运行Caffe验证
- **Given**: 从tar文件重新加载的caffe-cpu:jupyter镜像
- **When**: 运行容器执行镜像自带的verify-caffe.sh脚本
- **Then**: 验证脚本通过，Caffe核心功能正常
- **Verification**: `programmatic`

## Open Questions
- [ ] 导出的镜像文件名格式是否需要特定命名？（默认使用caffe-cpu-jupyter_YYYYMMDD.tar格式）
- [ ] 如果已有同名旧镜像，是否需要先删除旧镜像再构建？
- [ ] 构建过程中是否需要使用--no-cache强制重新构建？
