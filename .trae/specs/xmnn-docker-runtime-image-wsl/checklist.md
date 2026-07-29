# XMNN Docker 运行时镜像（WSL 构建） - Verification Checklist

## 环境就绪检查
- [ ] WSL2 Ubuntu 24.04 中 Docker 服务正常运行（`docker info` 无错误）
- [ ] wheel 文件存在于 Docker 构建上下文可访问的位置
- [ ] environment.yml 存在且 Python 版本为 3.14
- [ ] docker/entrypoint-runtime.sh 存在且可执行

## Dockerfile 适配检查
- [ ] Dockerfile.runtime 中 COPY wheel 路径与实际 wheel 位置一致
- [ ] Dockerfile.runtime 中 Python 版本与 wheel ABI 匹配（3.14）
- [ ] builder 阶段 conda 环境创建成功
- [ ] builder 阶段 pip install wheel 成功，所有依赖自动解析
- [ ] runtime 阶段包含必要系统库（libgomp1, libstdc++6 等）
- [ ] 多阶段构建正确：runtime 阶段不包含编译工具链
- [ ] .pth 初始化脚本（tvm_nuitka_init.pth, vta_nuitka_init.pth）正常安装

## 镜像构建检查
- [ ] `docker build` 成功完成（退出码 0）
- [ ] 镜像标签 `xmnn-runtime:1.2.2` 存在
- [ ] 镜像大小在合理范围（基础版 < 2GB）
- [ ] 构建日志中 builder 阶段验证步骤（import tvm/vta/xmnn）通过

## 核心功能验证
- [ ] `docker run --rm xmnn-runtime:1.2.2 python -c "import tvm; print(tvm.__version__)"` 输出 0.19.0
- [ ] `docker run --rm xmnn-runtime:1.2.2 python -c "import vta; print('VTA OK')"` 成功
- [ ] `docker run --rm xmnn-runtime:1.2.2 python -c "import xmnn; print(xmnn.__version__)"` 成功
- [ ] TE compute（te.placeholder + te.compute + te.create_schedule）在容器内执行成功
- [ ] Relay 表达式构建（relay.var + relay.nn.dense）在容器内执行成功
- [ ] NDArray 创建和 numpy 互操作在容器内执行成功
- [ ] 容器内 tvm/_libs 目录包含 11 个 .so 文件（2个原始+9个捆绑库）
- [ ] ldd 检查所有 .so 文件无 "not found" 依赖
- [ ] TVM_LIBRARY_PATH 环境变量正确指向 tvm/_libs
- [ ] numpy, scipy, ml_dtypes, Pillow, pandas, matplotlib 等依赖均可导入

## Entrypoint 和交互验证
- [ ] 容器工作目录为 /workspace
- [ ] entrypoint 脚本正确执行，输出启动日志
- [ ] UID/GID 自动检测和调整逻辑正常
- [ ] 默认 CMD (python) 可启动 Python 解释器
- [ ] `docker run -it --rm xmnn-runtime:1.2.2 bash` 可进入交互式 shell

## 安全和精简检查
- [ ] 运行时镜像中不存在 gcc/cmake/ninja 等编译工具
- [ ] 运行时镜像中不存在 Nuitka 编译器
- [ ] 镜像中不包含 TVM/VTA/XMNN Python 源码（仅 .so 编译产物）
- [ ] apt 缓存已清理（rm -rf /var/lib/apt/lists/*）
- [ ] conda clean 已执行
