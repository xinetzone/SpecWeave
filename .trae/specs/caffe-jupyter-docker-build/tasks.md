# Caffe Jupyter Docker镜像构建与导出 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 预构建环境检查与配置确认
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 确认WSL中Docker daemon正常运行
  - 确认caffe根目录结构完整（caffex/、docker/origin/下的所有必需文件）
  - 检查磁盘剩余空间（WSL挂载的Windows磁盘）
  - 检查是否存在旧的caffe-cpu:jupyter镜像并记录状态
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 在WSL中执行`docker info`返回成功，显示Server Version
  - `programmatic` TR-1.2: caffex/Makefile存在且可读取，docker/origin/config/下配置文件齐全
  - `programmatic` TR-1.3: 目标路径/mnt/d/BaiduSyncdisk/docker在WSL中可访问且有写入权限
- **Notes**: 如有旧镜像，根据用户决定是否删除；构建会自动使用缓存加速

## [ ] Task 2: 执行Docker镜像构建
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在WSL中切换到caffe根目录（/mnt/d/spaces/SpecWeave/projects/xuanspace/vendor/caffe）
  - 执行构建命令：`docker build -t caffe-cpu:jupyter --target runtime-jupyter -f docker/origin/Dockerfile.jupyter-ssh .`
  - 监控构建过程，记录关键输出
  - 处理可能的构建错误（网络问题、依赖缺失等）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: docker build命令退出码为0
  - `programmatic` TR-2.2: `docker images caffe-cpu:jupyter`显示镜像存在，TAG为jupyter
  - `programmatic` TR-2.3: 镜像大小合理（预计1-3GB）
- **Notes**: 构建时间可能较长（10-30分钟），取决于网络速度和是否有缓存；多阶段构建包含4个stage

## [ ] Task 3: 镜像功能验证（Caffe导入测试）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 运行临时容器验证Caffe Python绑定
  - 执行：`docker run --rm caffe-cpu:jupyter python -c "import caffe; print('Caffe version:', caffe.__version__)"`
  - 验证核心Python依赖（numpy、scipy、matplotlib等）可导入
  - 运行镜像自带的verify-caffe.sh验证脚本
- **Acceptance Criteria Addressed**: [AC-2, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: python -c "import caffe" 无错误退出
  - `programmatic` TR-3.2: 输出Caffe版本信息（1.0）
  - `programmatic` TR-3.3: verify-caffe.sh脚本执行通过
  - `programmatic` TR-3.4: numpy、scipy、matplotlib、protobuf均可正常导入
- **Notes**: 使用--rm参数确保测试容器自动清理

## [ ] Task 4: 镜像功能验证（Jupyter/SSH环境测试）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 验证Jupyter相关包安装正确
  - 验证SSH服务配置文件语法正确
  - 验证supervisord配置存在且正确
  - 验证entrypoint脚本语法正确
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: `docker run --rm caffe-cpu:jupyter jupyter --version`正常输出
  - `programmatic` TR-4.2: `docker run --rm caffe-cpu:jupyter sshd -t`返回OK
  - `programmatic` TR-4.3: 镜像内/usr/local/bin/entrypoint-jupyter.sh存在且可执行
  - `programmatic` TR-4.4: /etc/supervisor/conf.d/下jupyter.conf和sshd.conf存在
- **Notes**: 不需要实际启动Jupyter服务，只验证安装和配置正确

## [ ] Task 5: 导出Docker镜像到tar文件
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 生成带日期戳的镜像文件名：caffe-cpu-jupyter_YYYYMMDD.tar
  - 执行docker save命令导出镜像：`docker save -o /mnt/d/BaiduSyncdisk/docker/caffe-cpu-jupyter_YYYYMMDD.tar caffe-cpu:jupyter`
  - 验证导出文件存在且大小合理
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: docker save命令退出码为0
  - `programmatic` TR-5.2: 目标路径下.tar文件存在
  - `programmatic` TR-5.3: 文件大小>100MB（与docker images显示的SIZE匹配）
  - `programmatic` TR-5.4: 文件在Windows资源管理器D:\BaiduSyncdisk\docker中可见
- **Notes**: 导出时间取决于镜像大小和磁盘IO速度；使用WSL路径/mnt/d/对应Windows D盘

## [ ] Task 6: 验证导出镜像的可加载性
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 记录原始镜像ID以备对比
  - 删除本地caffe-cpu:jupyter镜像：`docker rmi caffe-cpu:jupyter`
  - 从tar文件加载镜像：`docker load -i /mnt/d/BaiduSyncdisk/docker/caffe-cpu-jupyter_YYYYMMDD.tar`
  - 验证加载后的镜像可正常运行Caffe导入测试
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-6.1: docker rmi命令成功删除镜像
  - `programmatic` TR-6.2: docker load命令成功，输出Loaded image ID
  - `programmatic` TR-6.3: 加载后`docker images caffe-cpu:jupyter`显示镜像存在
  - `programmatic` TR-6.4: 从新加载的镜像运行容器，import caffe成功
  - `programmatic` TR-6.5: verify-caffe.sh在加载后的镜像中运行通过
- **Notes**: 这是完整性验证的关键步骤，确保导出的镜像文件没有损坏

## [ ] Task 7: 构建结果总结与交付
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 汇总构建日志关键信息（构建时间、镜像大小、镜像ID）
  - 记录导出文件路径和大小
  - 记录镜像加载验证结果
  - 清理临时测试容器（如有遗留）
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 构建报告清晰记录镜像名称、标签、ID、大小
  - `human-judgement` TR-7.2: 导出文件路径和大小明确记录
  - `programmatic` TR-7.3: 无遗留的临时测试容器（`docker ps -a`无caffe相关测试容器）
- **Notes**: 最终交付物是可在D:\BaiduSyncdisk\docker找到的tar镜像文件
