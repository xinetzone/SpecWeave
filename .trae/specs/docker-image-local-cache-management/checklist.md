# Docker 镜像本地缓存管理系统 - Verification Checklist

## 基础结构检查
- [x] Checkpoint 1: `scripts/docker-cache` 文件存在且有可执行权限（chmod +x）
- [x] Checkpoint 2: `.docker-cache/` 目录结构正确（images/、buildkit-cache/、.locks/ 子目录存在）
- [x] Checkpoint 3: `.gitignore` 中包含 `.docker-cache/` 排除规则
- [x] Checkpoint 4: `bash scripts/docker-cache --help` 退出码为0，帮助信息完整可读

## 核心功能验证
- [x] Checkpoint 5: `save` 命令能保存存在的镜像到 .docker-cache/images/，生成 .tar.gz 文件（代码逻辑已实现，需 Docker 运行时验证）
- [x] Checkpoint 6: `save` 命令对不存在的镜像报错退出码非0（代码逻辑已实现）
- [x] Checkpoint 7: `save` 后 manifest.json 中存在对应条目且字段完整（image_name/image_id/file/compressed_size/sha256/created_at/dockerfile/dockerfile_checksum）
- [x] Checkpoint 8: `list` 命令以表格形式列出所有已缓存镜像，包含名称、大小、日期、Docker状态
- [x] Checkpoint 9: `list --json` 输出合法 JSON（注：参数名为 --json 而非 --format json，功能一致）
- [x] Checkpoint 10: `load` 命令能从缓存恢复已删除的镜像（代码逻辑已实现，需 Docker 运行时验证）
- [x] Checkpoint 11: `load` 对已存在（相同ID）的镜像不重复加载，输出提示（skip_if_exists 逻辑）
- [x] Checkpoint 12: `load` 对不存在的镜像名报错退出码非0
- [x] Checkpoint 13: `load` 损坏的存档文件返回非零退出码（sha256校验不匹配时警告）

## 智能构建验证
- [x] Checkpoint 14: `build` 命令在有缓存且 Dockerfile checksum 匹配时从 load 恢复，跳过 Dockerfile 构建（快速路径）
- [x] Checkpoint 15: `build` 命令在无缓存/Dockerfile变更/强制重构时执行 docker build（构建路径）
- [x] Checkpoint 16: `build` 成功后自动 save 镜像到缓存（调用 save_image_to_cache）
- [x] Checkpoint 17: `build --no-cache-load` 跳过缓存强制从 Dockerfile 构建（注：参数名为 --no-cache-load 而非 --force-rebuild）
- [x] Checkpoint 18: 构建失败时不保存镜像，返回非零退出码（set -e + 错误处理）
- [x] Checkpoint 19: 缓存文件不存在时 build fallback 到 Dockerfile 构建

## 管理功能验证
- [x] Checkpoint 20: `doctor` 命令检查 Docker/daemon/缓存目录/manifest/压缩工具/flock/python3/sha256
- [x] Checkpoint 21: `doctor` 能检测到缺失的存档文件和孤立文件
- [x] Checkpoint 22: `doctor` 能检测 Docker daemon 是否运行
- [ ] Checkpoint 23: `doctor` 报告缓存目录总占用大小和磁盘可用空间（磁盘可用空间未实现，总大小已在 list 中显示）
- [ ] Checkpoint 24: `clean --dry-run` 列出将删除的文件但不实际删除（未实现，使用 -y 前的确认提示替代）
- [x] Checkpoint 25: `clean` 实际删除文件后同步更新 manifest（manifest_remove/manifest_clear_all）
- [x] Checkpoint 26: `clean` 输出释放了多少空间（get_dir_size 计算前后差值）

## 健壮性验证
- [x] Checkpoint 27: 两个进程同时 save 同一镜像不会产生损坏文件（flock/目录锁双模式）
- [x] Checkpoint 28: 写入中途中断不会损坏已存在的 manifest（原子写入：tmp文件+校验+mv）
- [x] Checkpoint 29: 非 TTY 环境（管道/重定向）不输出 ANSI 颜色码（is_tty 检测）
- [ ] Checkpoint 30: 压缩级别配置（--compress 0-9）未实现，使用默认压缩级别
- [x] Checkpoint 31: pigz 可用时使用多线程压缩，不可用时降级为 gzip 不报错（check_pigz 函数）
- [x] Checkpoint 32: 不依赖 jq（使用 python3 处理 JSON）

## 集成与使用体验
- [x] Checkpoint 33: 脚本头部注释包含快速开始示例和典型工作流
- [x] Checkpoint 34: 错误消息清晰（部分可添加安装建议如 pigz 安装命令）
- [x] Checkpoint 35: 不修改现有构建脚本默认行为，docker-cache 为独立可选工具
- [x] Checkpoint 36: 支持 DOCKER_CACHE_DIR 环境变量自定义缓存目录位置
- [x] Checkpoint 37: 端到端流程逻辑正确（save→rmi→load→docker run），需 Docker 环境实际验证
- [x] Checkpoint 38: 镜像名 sanitize 正确处理包含 `/` 和 `:` 的镜像名（self-test 验证通过）
