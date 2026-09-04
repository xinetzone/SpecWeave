# xmnn-whl-builder 干净重编译模式 - Verification Checklist

## 代码变更检查
- [ ] build-wheel.sh 中 CLEAN_REBUILD 检测逻辑正确：CLEAN_REBUILD=1 时设置 CCACHE_DISABLE=1 并执行 ccache -z
- [ ] build-wheel.sh 干净模式有醒目的横幅日志输出
- [ ] build-wheel.sh 默认（CLEAN_REBUILD!=1）行为不变，ccache 正常启用
- [ ] Dockerfile builder 阶段添加了 ARG CLEAN_REBUILD=0 和 ENV CLEAN_REBUILD=${CLEAN_REBUILD}
- [ ] Dockerfile ARG/ENV 位置在 RUN build-wheel.sh 之前，确保环境变量生效
- [ ] build.sh 添加了 CLEAN_REBUILD=0 变量声明
- [ ] build.sh -h/--help 输出包含 --clean-rebuild/-C 选项说明
- [ ] build.sh 参数解析正确处理 -C/--clean-rebuild，设置 CLEAN_REBUILD=1 和 NO_CACHE=1
- [ ] build.sh 干净模式时 BUILD_ARGS 同时包含 --no-cache 和 --build-arg CLEAN_REBUILD=1
- [ ] build.sh 配置日志（log_kv）显示干净重编译模式状态
- [ ] .agents/rules/dockerfile.md 构建参数表更新了 CLEAN_REBUILD 参数说明
- [ ] .agents/rules/dockerfile.md ccache 章节补充了干净重编译子节

## 功能验证（端到端）
- [ ] `./build.sh -h` 帮助信息完整，含 --clean-rebuild/-C 说明
- [ ] 默认构建（不带 -C）正常完成，verify-wheel.sh 11/11 PASS
- [ ] 默认构建 ccache 正常工作，无 CLEAN REBUILD 横幅
- [ ] 干净模式构建（`./build.sh --clean-rebuild --cn -v`）成功
- [ ] 干净模式日志中出现 CLEAN REBUILD 醒目标识
- [ ] 干净模式 docker build 命令包含 --no-cache 和 --build-arg CLEAN_REBUILD=1
- [ ] 干净模式 verify-wheel.sh 11/11 PASS
- [ ] 干净模式下 docker run import tvm/vta/xmnn 正常
- [ ] 干净模式构建后再执行一次普通构建，ccache 仍有缓存可用（缓存未被破坏）
- [ ] /opt/xmnn-dist/ 中 wheel 文件存在且可被下游镜像使用
- [ ] 镜像 ENTRYPOINT 为空，CMD 正确打印版本信息

## 质量与规范检查
- [ ] 代码风格与现有项目一致（缩进、变量命名、日志函数使用）
- [ ] 所有变更遵循 AGENTS.md 中的核心约束（两阶段构建、bind mount、不 COPY 源码等）
- [ ] 没有引入新的依赖包
- [ ] 默认构建路径行为完全不变（向后兼容）
- [ ] Dockerfile 首行仍为 # syntax=docker/dockerfile:1.7-labs
- [ ] 构建上下文仍为 external/chaos/，bind mount 路径正确
