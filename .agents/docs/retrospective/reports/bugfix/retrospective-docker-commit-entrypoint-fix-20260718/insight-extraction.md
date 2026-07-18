# 洞察萃取：docker commit ENTRYPOINT 泄漏问题

## 一、关键发现

### 洞察1：docker commit 是"快照"而非"构建"，会保留运行时状态

**事实支撑**：`docker commit` 保存的是容器当前的完整Config（Entrypoint、Cmd、Env、WorkingDir、User、ExposedPorts等），它不会自动区分"临时配置"和"永久配置"。

**深层含义**：docker commit ≠ Dockerfile build。Dockerfile构建是声明式的（你显式声明ENTRYPOINT/CMD），docker commit是命令式快照（你得到的是容器当前状态的精确拷贝）。用docker commit做"增量更新"时，必须用 `--change` 显式覆盖那些不应被保留的配置项。

### 洞察2：保活模式的临时配置泄漏是通用陷阱

**事实支撑**：本项目中用 `--entrypoint /bin/bash -c "while true; do sleep 3600; done"` 作为保活手段，但这不是唯一模式。常见的保活模式还有：
- `tail -f /dev/null`
- `sleep infinity`
- 启动一个后台服务进程

所有这些保活配置如果被docker commit保存，都会导致镜像无法正常使用。

**深层含义**：凡是涉及"启动临时容器→修改容器→commit为新镜像"的工作流，都必须在commit时显式重置容器入口配置。这是docker commit的通用陷阱，不仅限于bash/sleep模式。

### 洞察3：错误信息与根因的语义距离导致诊断成本高

**事实支撑**：错误 `cannot execute binary file` 看起来像是文件损坏/权限问题/架构不匹配，但实际根因是命令组合语义错误（把二进制文件当脚本执行）。

**深层含义**：当Docker容器启动失败时，不要只看错误信息的字面意思，要理解ENTRYPOINT+CMD的组合语义。诊断步骤应该是：
1. `docker inspect IMAGE --format '{{.Config.Entrypoint}} {{.Config.Cmd}}'` 查看入口配置
2. 手动拼接ENTRYPOINT+CMD+用户参数，理解实际执行的命令
3. 对比预期行为，定位配置问题

## 二、5-Whys根因分析

- **Why1**：为什么 `docker run IMAGE bash` 报错？
  → 因为实际执行的是 `/bin/bash bash`，bash尝试把bash二进制当脚本执行

- **Why2**：为什么实际执行的是 `/bin/bash bash`？
  → 因为镜像的Entrypoint是 `["/bin/bash"]`，用户传入的bash被当作参数拼接

- **Why3**：为什么镜像的Entrypoint是 `/bin/bash`？
  → 因为docker commit保存了临时保活容器的 `--entrypoint /bin/bash` 配置

- **Why4**：为什么docker commit会保存临时配置？
  → 因为docker commit默认保存容器完整Config，且脚本没有用 `--change` 重置Entrypoint/Cmd

- **Why5（根因）**：为什么脚本没有重置Entrypoint/Cmd？
  → 因为开发者不知道/忽略了docker commit会完整保留运行时配置这一隐式行为，缺乏"commit时显式声明入口配置"的最佳实践意识

## 三、规律认知

### docker commit 工作流安全模式

当使用 `docker run → docker exec → docker commit` 模式进行镜像增量更新时，必须遵守：

1. **commit时永远显式声明ENTRYPOINT和CMD**：使用 `--change` 参数
2. **commit后验证镜像入口配置**：`docker inspect` 检查
3. **区分"构建镜像"和"快照容器"**：如果需要可重复构建，优先使用Dockerfile；docker commit仅适合快速原型/临时保存

```
docker run (临时容器，带保活入口)
    ↓
docker exec (修改容器内容)
    ↓
docker stop (停止容器)
    ↓
docker commit --change='ENTRYPOINT [...]' --change='CMD [...]'  ← 关键：显式重置入口
    ↓
docker inspect (验证入口配置正确)
    ↓
docker run --rm IMAGE <测试命令> (验证镜像可用)
```
