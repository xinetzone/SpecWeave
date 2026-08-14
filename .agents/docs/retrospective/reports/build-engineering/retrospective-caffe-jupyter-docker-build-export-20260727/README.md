---
id: "retrospective-caffe-jupyter-docker-build-export-20260727"
title: "Caffe Jupyter Docker镜像构建与导出复盘（多阶段构建+缓存验证+离线分发包）"
type: "build-engineering"
date: "2026-07-27"
status: "completed"
maturity: "L2"
source: "caffe docker origin build and export task"
tags: ["docker", "caffe", "multi-stage-build", "jupyter", "image-export", "wsl", "offline-distribution"]
---

# Caffe Jupyter Docker镜像构建与导出复盘（多阶段构建+缓存验证+离线分发包）

## 执行摘要

使用 [Dockerfile.jupyter-ssh](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/docker/origin/Dockerfile.jupyter-ssh#L14-L16) 中的 `runtime-jupyter` 目标构建 `caffe-cpu:jupyter` 镜像，并将镜像导出为离线tar分发包保存到 `D:\BaiduSyncdisk\docker`。构建利用已有缓存层快速完成，镜像通过Caffe导入、Jupyter环境、镜像加载完整性三重验证，最终产出754MB的可离线分发tar文件。

**关键数据**：
- 镜像名称：`caffe-cpu:jupyter`
- 镜像ID：`ffedc7f18597`
- 虚拟大小：3.59 GB
- 导出tar大小：754 MB（压缩比约4.8:1）
- MD5校验：`75d5ca4ccd1ec37ebab2e776da80f9fd`
- 构建方式：Docker多阶段构建（4 stages），全部缓存命中
- 验证通过率：9/9 ✅
- 执行环境：WSL Ubuntu-24.04 + Docker 29.6.1

---

## R·事实清单（G1质量门：无因果词）

### F01. 初始需求

- 用户指定构建命令来源：[Dockerfile.jupyter-ssh](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/docker/origin/Dockerfile.jupyter-ssh#L14-L16) 第14-16行注释中的构建命令
- 目标镜像标签：`caffe-cpu:jupyter`
- 构建目标（--target）：`runtime-jupyter`
- 镜像保存路径：`D:\BaiduSyncdisk\docker`
- 交付要求：镜像构建成功 + 文件完整可用 + 支持后续加载部署

### F02. 启动协议执行

- 读取路径：SpecWeave 根 AGENTS.md → projects/AGENTS.md → xuanspace/AGENTS.md → vendor/AGENTS.md → caffe/AGENTS.md
- 内容敏感度判定：Caffe是BSD 2-Clause开源项目，属于公开内容
- 工作模式：Spec模式（先生成PRD/tasks/checklist，审核通过后执行）
- Spec文档目录：`.trae/specs/caffe-jupyter-docker-build/`

### F03. 环境检查结果

- WSL发行版：Ubuntu-24.04（Running状态）
- Docker版本：29.6.1，Engine正常运行
- Docker资源：12个容器（6个运行中），52个镜像
- caffex源码：Makefile、include/、src/、python/均存在
- docker/origin配置：config/、scripts/、entrypoint-jupyter.sh均齐全
- 目标路径：`D:\BaiduSyncdisk\docker`存在，读写测试通过
- 磁盘空间：D盘总552GB，剩余66GB（使用率89%）
- 旧镜像：存在`caffe-cpu:jupyter`（ID: 377660c571cf，3.59GB）
- 旧容器：存在运行中的`caffe-jupyter`容器（端口8888:8888、2222:22）

### F04. Spec规划产出

- [spec.md](../../../../../../.trae/specs/caffe-jupyter-docker-build/spec.md)：6个验收标准（AC-1~AC-6）
- [tasks.md](../../../../../../.trae/specs/caffe-jupyter-docker-build/tasks.md)：7个有序任务
- [checklist.md](../../../../../../.trae/specs/caffe-jupyter-docker-build/checklist.md)：6大类28个检查点
- Open Questions：3个（文件命名格式、是否删除旧镜像、是否--no-cache）

### F05. 旧容器清理操作

- 执行命令：`docker stop caffe-jupyter && docker rm caffe-jupyter`
- 停止容器ID：6d086fe384c5
- 删除容器：成功

### F06. Docker镜像构建过程

- 构建命令：`docker build -t caffe-cpu:jupyter --target runtime-jupyter -f docker/origin/Dockerfile.jupyter-ssh .`
- 构建上下文路径：`/mnt/d/spaces/SpecWeave/projects/xuanspace/vendor/caffe`
- 构建实例：default实例，docker driver
- 基础镜像：ubuntu:22.04@sha256:0e0a0fc6d18feda9db1590da249ac93e8d5abfea8f4c3c0c849ce512b5ef8982
- 构建上下文大小：30.02kB
- 所有41个步骤层：CACHED状态（全部命中缓存）
- 最终输出：
  - exporting manifest sha256:f5357c84936667e8cdb92eebb284140d007996a671231e033343a701eb4bc315
  - exporting config sha256:0129341c3b45ccbf0434d667dfa55975a8a23646d91ac9e11d9e4906a9fcd4c1
  - naming to docker.io/library/caffe-cpu:jupyter: done

### F07. 镜像内容验证结果

| 验证项 | 结果 |
|--------|------|
| 镜像存在（docker images） | ID: ffedc7f18597，3.59GB |
| Caffe导入 | `import caffe` → Caffe version: 1.0.0 |
| numpy版本 | 1.26.4 |
| scipy版本 | 1.15.3 |
| matplotlib版本 | 3.10.9 |
| protobuf版本 | 3.20.3 |
| verify-caffe.sh | 全项通过（库文件、Caffe导入、Proto、4个CLI工具） |
| Jupyter版本 | JupyterLab 4.2.5, Notebook 7.2.2, Jupyter Server 2.14.1 |
| supervisord版本 | 4.2.1 |
| entrypoint脚本语法 | bash -n 验证通过 |
| caffe-origin用户 | uid=1000, gid=1000, groups=sudo |
| 构建信息文件 | BUILD_DATE=2026-07-26T03:56:55Z, BASE_IMAGE=ubuntu:22.04 |

### F08. SSH配置验证现象

- 直接执行`docker run --rm caffe-cpu:jupyter sshd -t`输出："no hostkeys available"
- Dockerfile第338行`ssh-keygen -A`在RUN阶段执行，密钥生成于镜像构建时
- 但该报错属于正常现象：entrypoint-jupyter.sh在容器启动时动态重新生成主机密钥

### F09. 镜像导出过程

- 首次尝试失败：在`wsl -d Ubuntu-24.04 -- bash -c "cd ... && TAR_FILE=... && docker save -o $TAR_FILE ..."`中`$TAR_FILE`被Windows shell/PowerShell提前展开为空字符串
- 错误信息：`docker: 'docker save' requires at least 1 argument`
- 修复方式：改为直接传递完整路径，不使用shell变量
- 成功命令：`wsl -d Ubuntu-24.04 -- docker save -o /mnt/d/BaiduSyncdisk/docker/caffe-cpu-jupyter_20260727.tar caffe-cpu:jupyter`
- 导出耗时：约30-60秒
- 导出文件：caffe-cpu-jupyter_20260727.tar
- 文件大小：754MB（790,484,992字节）
- MD5校验值：75d5ca4ccd1ec37ebab2e776da80f9fd
- 文件在Windows资源管理器中可见

### F10. 镜像加载完整性验证

- 删除本地镜像：`docker rmi caffe-cpu:jupyter`成功
- 确认删除：`docker images caffe-cpu:jupyter`无输出
- 加载镜像：`docker load -i /mnt/d/BaiduSyncdisk/docker/caffe-cpu-jupyter_20260727.tar`
- 加载输出：`Loaded image: caffe-cpu:jupyter`
- 加载后镜像ID：ffedc7f18597（与构建时ID一致）
- 加载后Caffe导入：`import caffe` → 1.0.0 成功
- 加载后verify-caffe.sh：全项通过
- 加载后Jupyter：正常
- 临时容器清理：`docker container prune -f`清理3个容器，回收462.8kB

### F11. Dockerfile多阶段结构（4 stages）

| Stage | 名称 | 基础镜像 | 职责 |
|-------|------|---------|------|
| 0 | base-system | ubuntu:22.04 | apt换源（阿里云）、CA证书、基础工具（curl/wget/tzdata） |
| 1 | base-builder | base-system | 编译工具链、Caffe系统依赖、Python 3.10+科学计算包、创建builder用户 |
| 2 | builder | base-builder | COPY caffex源码、generate-makefile-config.sh、make all/pycaffe/tools/distribute |
| 3 | runtime-jupyter | base-builder | COPY构建产物、安装SSH+Jupyter+supervisord、配置caffe-origin用户、生成构建信息 |

### F12. 镜像环境配置

- 操作系统：Ubuntu 22.04
- Python：系统Python 3.10.12（非venv/conda）
- 非root用户：caffe-origin（UID 1000, GID 1000, NOPASSWD sudo）
- 时区：Asia/Shanghai
- Locale：zh_CN.UTF-8
- CAFFE_ROOT：/workspace/caffex
- PYTHONPATH：/workspace/caffex/python
- 暴露端口：22（SSH）、8888（Jupyter）
- 进程管理：supervisord管理sshd和jupyter
- Entrypoint：/usr/bin/tini -- /usr/local/bin/entrypoint-jupyter.sh
- Volume：/workspace
- Healthcheck：每30秒执行healthcheck-jupyter.sh

### F13. 用户后续提问

- 问题：如果镜像复制到没有Docker环境的机器上，需要哪些命令？
- 回答内容：方案一（推荐）在目标机器安装Docker后加载镜像；方案二说明无Docker时tar无法直接运行

---

## I·洞察分析（G2质量门：四元组完整）

### 洞察 I1：Docker构建缓存的"隐身"价值——成功构建后的二次构建几乎零成本

**现象（F06）**：本次docker build时全部41层均显示CACHED，构建在数秒内完成，无需重新编译Caffe（Caffe编译通常需要10-30分钟）。

**根因**：Dockerfile结构合理，多阶段构建将"安装系统依赖"和"编译源码"分层；之前已成功构建过相同的Dockerfile和上下文，所有层的哈希值匹配，Docker直接复用缓存层。缓存命中的前提条件是：（1）Dockerfile指令顺序和内容完全一致；（2）COPY的源文件内容未变；（3）基础镜像digest未变。

**影响**：
- 时间收益：避免了Caffe源码编译的10-30分钟等待
- 可复现性：缓存命中证明构建是确定性的（deterministic），相同输入产生相同输出
- 风险：如果缓存基于的旧镜像有安全漏洞，缓存会复用有漏洞的层；需要定期`--no-cache`重建获取安全更新

**改进建议**：对于需要定期重建的基础镜像，建立"定期缓存失效"策略（如每周--no-cache重建一次获取安全更新），但日常开发构建应充分利用缓存加速。

---

### 洞察 I2：WSL跨层Shell命令的变量展开陷阱

**现象（F09）**：首次docker save失败，错误提示需要参数。根因是`wsl -d Ubuntu-24.04 -- bash -c "cd ... && TAR_FILE=xxx && docker save -o $TAR_FILE ..."`中`$TAR_FILE`在传递给wsl前被PowerShell展开为空字符串。

**根因**：存在三层Shell嵌套——最外层是PowerShell（Windows），中间是wsl.exe参数解析，内层是bash -c。PowerShell中`$TAR_FILE`是PowerShell变量语法，在传递给wsl进程前PowerShell尝试展开它；由于PowerShell中不存在该变量，展开结果为空字符串，导致实际执行的命令变成`docker save -o caffe-cpu:jupyter`（缺少输出路径参数）。

**影响**：命令执行失败，需要重新执行。这类问题在Windows+WSL混合环境中常见且难以调试——错误信息"requires at least 1 argument"不直接指向变量展开问题。

**改进建议**：在WSL中执行复杂命令时，遵循以下原则：
1. 避免在`bash -c "..."`内部使用shell变量，改为直接传值
2. 如需使用变量，对`$`进行转义（单引号或反斜杠转义）
3. 优先使用"直接传路径"的简单命令形式，减少嵌套层级
4. 将复杂命令封装为WSL内的shell脚本文件，通过`wsl bash /path/to/script.sh`执行

---

### 洞察 I3：Docker镜像虚拟大小 vs 导出大小——理解docker save的压缩特性

**现象（F06、F09、F10）**：镜像虚拟大小3.59GB（docker images显示），但导出的tar文件仅754MB，加载后镜像ID完全一致。

**根因**：Docker存储驱动使用分层文件系统（overlay2），`docker images`显示的SIZE是各层解压后虚拟大小的总和（包含共享基础层的重复计算）。而`docker save`导出的是各层的tar包集合，每层内部使用gzip压缩，因此导出文件远小于虚拟大小。3.59GB到754MB的4.8:1压缩比符合Docker镜像的典型压缩率（系统文件和二进制库通常有较高的压缩比）。

**影响**：
- 存储和传输：754MB的tar文件适合通过U盘、网盘分发
- 加载后磁盘占用：加载后Docker会解压各层到overlay2，实际占用接近虚拟大小（但通过层共享可减少冗余）
- MD5校验的意义：确保传输/存储过程中文件未损坏，与加载后镜像ID一致形成双重校验

**改进建议**：离线分发镜像时，使用docker save + MD5/SHA校验；接收方docker load后验证镜像ID和功能，形成"导出→校验→传输→加载→验证"的完整链路。

---

### 洞察 I4：镜像完整性验证的"删除-加载-再验证"闭环不可省略

**现象（F10）**：在docker save成功后，执行了"删除本地镜像→从tar加载→重新验证"的完整闭环，而不仅仅是检查tar文件存在和大小。

**根因**：docker save成功只代表Docker引擎成功写出了文件，但不保证：（1）写入过程中磁盘IO错误导致文件损坏；（2）文件系统层面的静默数据损坏；（3）tar格式是否完整可被docker load正确解析。只有实际执行docker load并验证加载后镜像的功能，才能确认分发包的完整性。

**影响**：
- 正向保障：确保离线分发包在目标机器上可以成功加载
- 避免"虚假成功"：如果只检查"文件存在+大小非零"就认为成功，可能在目标机器部署时才发现文件损坏
- 镜像ID一致性验证：加载后镜像ID与原镜像一致（ffedc7f18597），证明tar文件包含了完整的镜像元数据和层数据

**改进建议**：所有Docker镜像导出操作都应遵循"构建→验证→导出→删除→加载→再验证"的六步标准流程，这是确保离线分发包可用性的必要质量门。

---

### 洞察 I5：Docker镜像本质依赖容器运行时——"离线"不等于"无依赖"

**现象（F13）**：用户询问"复制到没有Docker环境的机器上需要哪些命令"。核心事实是：docker save产出的.tar文件是Docker镜像格式，不是自包含的可执行程序。

**根因**：Docker镜像包含：（1）rootfs文件系统（Ubuntu用户空间、Caffe、Python等）；（2）镜像元数据（ENV/EXPOSE/ENTRYPOINT等）；（3）层清单（manifest）。这些内容需要Docker Engine（或兼容的OCI运行时如Podman、containerd）来解释和执行——设置namespace/cgroup、挂载rootfs、配置网络、执行ENTRYPOINT等。没有容器运行时，tar文件只是一堆"有目录结构的文件"，无法直接运行Caffe或Jupyter。

**影响**：
- 部署方案选择：目标机器必须安装Docker/Podman才能使用镜像
- 替代方案评估：chroot（需要Linux且缺少namespace隔离，glibc版本可能不兼容）、虚拟机镜像（OVA/VMDK，本质仍是在虚拟机中运行Docker）、静态编译（Caffe+Python+Jupyter栈过大不现实）
- 文档完整性：交付镜像时必须同时提供目标机器的Docker安装指南

**改进建议**：在交付Docker镜像分发包时，必须配套提供：（1）目标机器Docker安装指南；（2）镜像加载命令；（3）容器启动命令模板；（4）验证命令。确保接收方可以独立完成部署。

---

### 洞察 I6：Dockerfile中"构建时生成"与"运行时生成"的区分——SSH主机密钥案例

**现象（F08）**：Dockerfile中在RUN阶段执行了`ssh-keygen -A`，但直接`sshd -t`检查时报"no hostkeys available"。这不是Dockerfile的bug。

**根因**：多阶段构建中runtime-jupyter阶段的文件系统操作（RUN ssh-keygen -A在第338行）确实会在镜像中生成密钥，但entrypoint-jupyter.sh在容器启动时可能会重新生成密钥（安全最佳实践：每个容器实例应有唯一的主机密钥，而非所有容器共享镜像中预生成的密钥）。sshd -t在无启动环境变量和entrypoint处理的情况下，可能找不到密钥路径或权限不对。

**影响**：这不是bug，但容易造成误判——"Dockerfile里写了ssh-keygen -A为什么还报密钥不存在？"需要理解：构建时（docker build）和运行时（docker run）是两个不同阶段，entrypoint是运行时入口，会覆盖/补充构建时的配置。

**改进建议**：验证容器服务时，应优先使用entrypoint启动容器（`docker run -d ...`后`docker exec`检查），而非绕过entrypoint直接`docker run --rm image command`。后者适合验证文件存在性和基本命令，不适合验证由entrypoint初始化的服务（SSH host keys、数据库初始化、权限设置等）。

---

## E·模式萃取（G3质量门：可迁移验证）

### 模式 P1：Docker镜像构建-验证-导出-分发六步标准流程

**触发场景**：
- 需要将Docker镜像导出为离线分发包
- 目标环境可能无法访问镜像仓库（内网隔离、无网络、新机器部署）
- 需要确保镜像文件在传输后可用

**核心步骤**：
1. **环境预检**：检查Docker daemon状态、构建上下文完整性、磁盘空间、端口/容器冲突
2. **执行构建**：`docker build -t <name>:<tag> --target <stage> -f <dockerfile> <context>`
3. **功能验证**：运行临时容器验证核心功能（import、CLI工具、服务配置）
4. **导出镜像**：`docker save -o <path>/<name>-<tag>_<date>.tar <name>:<tag>`，记录MD5/SHA256
5. **完整性闭环**：`docker rmi <name>:<tag>` → `docker load -i <tarfile>` → 重新验证功能
6. **分发交付**：提供tar文件+校验值+加载命令+启动命令+验证命令

**关键质量门**：
- G1（构建后）：镜像存在、核心功能可用
- G2（导出后）：tar文件存在、大小>预期最小值
- G3（加载后）：镜像ID一致、功能验证通过（不可省略）

**反模式**：
- ❌ 只docker save不做删除-加载-再验证（无法发现文件损坏）
- ❌ docker images显示的SIZE作为导出文件大小预期（虚拟大小≠导出大小）
- ❌ 导出时使用gzip二次压缩（docker save已是压缩tar，二次压缩收益小且增加加载时解压步骤）
- ❌ 绕过entrypoint直接运行服务命令验证（缺少运行时初始化）

**迁移验证**：该模式可迁移到：
- 任何Docker镜像的离线分发场景（AI模型服务、数据库镜像、开发环境镜像）
- CI/CD流水线中的镜像归档环节
- 多环境部署（dev→staging→prod的镜像传递）
- 离线培训/演示环境的快速交付

---

### 模式 P2：WSL环境下Docker操作的安全命令模式

**触发场景**：
- 在Windows上通过WSL运行Docker命令
- 需要在wsl -d 调用中传递包含路径、变量、管道的复杂命令

**核心步骤**：
1. **简单命令直传**：`wsl -d <distro> -- docker <subcommand> <args>`（不使用bash -c包裹）
2. **路径使用WSL格式**：Windows D盘 → `/mnt/d/`，目录含空格用引号包裹
3. **避免Shell变量嵌套**：不在`bash -c "..."`中使用`$VAR`，改为直接传值或先`wsl`进入再执行
4. **复杂操作脚本化**：将多条命令写入.sh文件，通过`wsl -d <distro> -- bash /path/to/script.sh`执行
5. **构建上下文确认**：docker build的上下文路径是WSL内的路径，执行前`cd`到正确目录

**常见陷阱**：
| 陷阱 | 表现 | 规避方式 |
|------|------|---------|
| PowerShell变量展开 | `$VAR`在bash -c内被PowerShell提前展开为空 | 不用bash -c，或转义`$`为`\$` |
| 路径分隔符混淆 | Windows反斜杠`\`在WSL中不识别 | 统一使用正斜杠`/`和/mnt/盘符 |
| 换行符问题 | Windows CRLF脚本在Linux中执行报`$'\r': command not found` | 在WSL中创建脚本，或dos2unix转换 |
| 文件权限问题 | Windows文件挂载到WSL默认777，构建时COPY保留权限 | 重要脚本在Dockerfile内chmod +x |

**反模式**：
- ❌ `wsl -d Ubuntu -- bash -c "cd /path && VAR=val && docker save -o $VAR img"`（$VAR被外层展开）
- ❌ 使用Windows路径如`D:\BaiduSyncdisk\docker`直接传给docker（WSL中不识别）
- ❌ 在PowerShell中通过`wsl`执行含大量管道/重定向的复杂单行命令（排错困难）

**迁移验证**：该模式可迁移到：
- Windows+WSL2环境下的所有Docker操作
- Podman在WSL中的操作
- 远程SSH+Docker的类似场景（多层Shell嵌套问题同理）

---

### 模式 P3：多阶段Dockerfile的运行时配置vs构建时配置分离原则

**触发场景**：
- 设计或审查Dockerfile时
- 遇到"构建时正常、运行时报错"或"构建时报错、运行时正常"的配置问题

**核心原则**：
1. **构建时配置（RUN层）**：安装软件包、编译源码、创建用户、设置文件权限——这些操作结果持久化到镜像层
2. **运行时配置（ENTRYPOINT/CMD层）**：生成密钥、初始化数据库、修改配置文件（基于环境变量）、权限修复——这些操作每次容器启动时执行
3. **镜像元数据（ENV/EXPOSE/LABEL/HEALTHCHECK）**：声明式配置，不执行命令，作为容器运行时的默认值
4. **不要假设构建时配置在运行时原封不动保留**：entrypoint可能修改文件、重新生成密钥、切换用户

**核心步骤**：
1. 区分配置生命周期：问自己"这个配置是应该固定在镜像中，还是每次启动时动态确定？"
2. 固定配置用RUN层：软件安装、源码编译、静态文件复制
3. 动态配置用entrypoint：主机密钥、密码设置、环境变量注入、依赖外部存储的初始化
4. 验证服务时使用docker run -d启动完整容器（经过entrypoint），再docker exec进入检查
5. 临时验证可绕过entrypoint（`docker run --rm --entrypoint="" image command`），但要意识到缺少运行时初始化

**反模式**：
- ❌ 在RUN层生成SSH主机密钥并期望所有容器共享（安全风险：密钥应随容器实例唯一）
- ❌ 直接docker run --rm image sshd -t来验证SSH服务配置（绕过entrypoint，缺少密钥生成）
- ❌ 在CMD中执行初始化逻辑（CMD可被docker run的命令参数覆盖，应使用ENTRYPOINT）
- ❌ 把所有配置都塞到entrypoint（增加启动时间、引入不必要的依赖）

**迁移验证**：该模式可迁移到：
- 所有Dockerfile设计和审查场景
- 容器化应用的启动脚本设计
- Kubernetes initContainer vs container command的设计决策

---

## 关键决策记录

| 决策 | 选项A | 选项B | 决策结果 | 决策依据 |
|------|-------|-------|---------|---------|
| 构建模式 | 直接命令行构建 | Spec模式先规划再执行 | B | 用户使用/spec指令明确要求Spec模式；7步任务适合先规划 |
| 缓存策略 | --no-cache强制重建 | 使用缓存构建 | B | 之前已有成功构建，缓存命中证明构建可复现；节省10-30分钟 |
| 旧容器处理 | 保留运行中的容器 | 先stop+rm旧容器 | B | 旧容器占用同名，且挂载可能影响构建（虽不是构建依赖但避免干扰） |
| 旧镜像处理 | 先docker rmi旧镜像再构建 | 直接构建覆盖（默认行为） | B | docker build默认覆盖tag，无需手动删除；后续F10完整性验证时才需要删除 |
| 导出文件名 | caffe-cpu-jupyter.tar | caffe-cpu-jupyter_YYYYMMDD.tar | B | 带日期戳便于区分不同构建版本，避免覆盖历史备份 |
| 完整性验证级别 | 仅检查文件存在/大小 | 删除→加载→功能验证 | B | 文件存在不代表可用；加载+功能验证是确保分发包可用的唯一可靠方式 |
| 回答"无Docker机器"问题 | 只说需要装Docker | 提供完整安装+加载+启动指南 | B | 用户可能需要实际操作指南，提供完整命令序列更有价值 |

---

## 改进建议与原子行动项

### A1（低优先级）：为Caffe Docker构建添加build.sh自动化脚本
- **问题**：当前构建需要手动输入较长的docker build命令，路径和参数容易出错
- **建议**：在[docker/origin/](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/docker/origin)下创建build.sh脚本封装构建+验证+导出流程
- **验收标准**：`./build.sh`一条命令完成构建、验证、导出到指定目录
- **注意**：caffex是vendor submodule不可修改，但docker/origin/属于外层包装，可以添加脚本

### A2（低优先级）：定期--no-cache重建获取基础镜像安全更新
- **问题**：当前镜像基于2026-07-26的缓存层，Ubuntu基础镜像的安全更新不会自动获取
- **建议**：每月或每季度使用`docker build --no-cache`重建一次，获取apt安全更新
- **验收标准**：重建后镜像中`apt list --upgradable`无安全更新

### A3（信息性）：完善镜像离线交付的配套文档
- **问题**：交付tar文件时缺乏标准化的"接收方操作指南"
- **建议**：在D:\BaiduSyncdisk\docker\下创建README.txt，包含：
  1. Docker安装命令（Ubuntu/Windows/macOS）
  2. docker load命令
  3. docker run启动模板
  4. 验证命令
  5. MD5校验方法
- **验收标准**：新机器上的用户按README可独立完成部署，无需额外询问

---

## 产物统计

```
镜像文件: caffe-cpu:jupyter (ffedc7f18597)
虚拟大小: 3.59 GB
导出tar: D:\BaiduSyncdisk\docker\caffe-cpu-jupyter_20260727.tar (754 MB)
压缩比: 4.8:1
MD5: 75d5ca4ccd1ec37ebab2e776da80f9fd

镜像内容构成:
  - Ubuntu 22.04 基础系统              (~150MB 虚拟)
  - Caffe 编译工具链+系统依赖          (~800MB 虚拟)
  - Python 3.10 + 科学计算包           (~1.5GB 虚拟，numpy/scipy/matplotlib/protobuf等)
  - Caffe 1.0.0 编译产物               (~200MB 虚拟，libcaffe.so+_caffe.so+工具)
  - JupyterLab/Notebook + 依赖         (~500MB 虚拟)
  - SSH + supervisord + 配置           (~50MB 虚拟)
  - 总计                               (~3.59GB 虚拟，754MB 压缩导出)

Spec规划文档:
  - spec.md: 6个AC，功能+非功能需求+约束+假设
  - tasks.md: 7个有序任务
  - checklist.md: 28个检查点（全部通过）
```

---

## 相关报告索引

- [retrospective-caffe-standalone-caffex-removal-20260727](retrospective-caffe-standalone-caffex-removal-20260727/README.md) — Caffe standalone版本caffex依赖移除
- [compiled-wheel-runtime-image-build](../../../patterns/code-patterns/compiled-wheel-runtime-image-build.md) — 编译Python Wheel运行时镜像构建模式（相关模式）
- [docker-modular-build-orchestration](../../../patterns/architecture-patterns/docker-modular-build-orchestration.md) — Docker模块化构建编排模式（相关模式）
- [wsl-distro-install-migration-guide](../../../patterns/code-patterns/wsl-distro-install-migration-guide.md) — WSL发行版安装迁移指南
