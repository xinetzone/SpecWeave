# 导出建议：可复用模式与行动项

## 一、可复用模式

### 模式：docker commit 镜像配置重置

**模式ID**：docker-commit-config-reset
**模式名称**：docker commit 入口配置显式重置
**模式类型**：code-pattern
**成熟度**：L1-draft（单案例验证）

**触发场景**：
- 当使用 `docker run → docker exec → docker commit` 工作流做镜像增量更新时
- 临时容器使用了保活入口（bash/sleep/tail等），需要commit为正式镜像

**核心做法**：
1. 在 `docker commit` 命令中使用 `--change='ENTRYPOINT []'` 清空入口点
2. 使用 `--change='CMD ["/bin/bash"]'` （或其他合适的默认命令）设置默认命令
3. commit后使用 `docker inspect` 验证配置
4. 使用 `docker run --rm IMAGE <测试命令>` 验证镜像可用性

**反模式**：
- ❌ 直接 `docker commit $CONTAINER $IMAGE` 不做任何配置重置
- ❌ 在docker run时才用 `--entrypoint ''` 绕过问题（治标不治本，每个使用者都要知道这个workaround）
- ❌ 使用 `docker commit --change='ENTRYPOINT ["/bin/bash"]'` 但不清空CMD（会保留sleep等保活命令）

**检验标准**：
- `docker inspect IMAGE --format '{{.Config.Entrypoint}}'` 输出为空或正确的入口脚本
- `docker inspect IMAGE --format '{{.Config.Cmd}}'` 输出为合理的默认命令（如["/bin/bash"]）
- `docker run --rm IMAGE bash -c "echo ok"` 能正常执行

## 二、改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| docker commit 隐式保留临时配置 | 已在两个导出脚本中添加--change重置ENTRYPOINT/CMD | 高 | 新导出的镜像不再有入口配置问题 | 已完成 |
| 现有镜像存在错误配置 | 已修复xmnn-runtime:1.2.1-fix-cp314镜像 | 高 | 当前镜像可正常使用 | 已完成 |
| 缺乏镜像配置验证步骤 | 在导出脚本commit后添加inspect验证步骤，自动检查Entrypoint/Cmd合理性 | 中 | 提前发现配置问题，避免交付坏镜像 | 待规划 |
| 其他docker commit使用点可能存在同样问题 | 检查项目中所有使用docker commit的脚本，统一修复 | 中 | 防止同类Bug在其他脚本中出现 | 待规划 |

## 三、行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | 修复现有导出脚本 | do_export.sh和export_runtime.sh的docker commit添加--change参数 | 2026-07-18 | 已完成 |
| 高 | 修复当前镜像 | 重新commit xmnn-runtime:1.2.1-fix-cp314修复ENTRYPOINT/CMD | 2026-07-18 | 已完成 |
| 中 | 检查其他docker commit使用点 | Grep搜索项目中所有docker commit，检查是否需要添加--change | 2026-07-19 | 待规划 |
| 中 | 添加commit后验证步骤 | 在导出脚本commit后添加inspect+test验证 | 2026-07-19 | 待规划 |
| 低 | 沉淀docker commit最佳实践到知识库 | 将本模式归档到code-patterns目录 | 2026-07-18 | 进行中 |

## 四、模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 | 验证/复用次数 |
|---------|-----------|---------|---------|-------------|
| docker-commit-config-reset | 新增 L1-draft | 本次Bug修复 | 2026-07-18 | 1 |
