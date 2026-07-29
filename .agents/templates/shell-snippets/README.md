# Shell Snippets 可复用模板

面向 Bash/PowerShell/WSL2 开发场景的即用型代码模板，从实战复盘中萃取，可直接复制使用。

## 模板索引

| 模板文件 | 用途 | 对应模式 |
|----------|------|----------|
| [bash-structured-logging.sh](bash-structured-logging.sh) | Bash 统一结构化日志库（text+json双格式，metric/event/summary） | bash-unified-structured-logging |
| [powershell-wsl-wrapper.ps1](powershell-wsl-wrapper.ps1) | PowerShell→WSL 跨Shell脚本包装器（自动检测+路径转换+参数透传） | powershell-wsl-cross-shell-wrapper |
| [wsl2-docker-selection.md](wsl2-docker-selection.md) | WSL2 Docker 方案选择文档模板（性能对比表+决策矩阵） | wsl2-docker-selection-decision |

## 快速复用

### 1. Bash 日志库

```bash
# 将 bash-structured-logging.sh 复制到你的项目 scripts/lib/logging.sh
# 修改默认 LOG_SERVICE 名称后，在脚本中加载：

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="my-service"

# 参数解析中添加日志参数支持
while [[ $# -gt 0 ]]; do
    case "$1" in
        --log-format=*) LOG_FORMAT="${1#*=}"; shift ;;
        --log-level=*)  LOG_LEVEL="${1#*=}"; shift ;;
        --log-json)     LOG_JSON_STDOUT=1; shift ;;
        # ... 其他参数
    esac
done

# 使用
log_step "阶段 1/3: 环境检查"
log_info "Docker 可用"
log_ok "前置条件满足"
log_metric "build_duration" 42 "seconds"
log_event "deploy_complete" "status=success"
log_summary 8 0 8 280 "success"
```

### 2. PowerShell WSL 包装器

```powershell
# 将 powershell-wsl-wrapper.ps1 复制为你的项目包装器（如 deploy.ps1）
# 修改配置区的 $BashScript 路径和业务参数
# 运行：
.\deploy.ps1                    # 默认text输出
.\deploy.ps1 -LogFormat json    # JSON格式（监控采集）
```

### 3. Docker 方案选择文档

```markdown
<!-- 将 wsl2-docker-selection.md 内容复制到你的部署文档"Docker环境"章节 -->
<!-- 根据实际硬件运行基准测试，替换性能对比表中的占位数据 -->
```
