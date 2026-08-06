# xmtools 全面复盘 + whl 打包 + Docker 镜像导出 Checklist

## 阶段 1：复盘

- [x] 事实清单已输出（≥20 条，无因果词，编号 F-001 起）
- [x] 代码结构审查完成（pyproject/CMakeLists/tasks.py/docker/scripts/sdk/.agents）
- [x] 功能模块评估完成（6 大模块）
- [x] 潜在问题已按 P0/P1/P2 分级列出
- [x] 性能优化建议已给出（体积/耗时/加载）
- [x] 洞察 ≥3 条，每条含四元组（陈述/证据/反常识/行动）
- [x] 模式萃取 ≥2 个，含触发/步骤/反模式/检验/迁移
- [x] V 对抗审查完成（4 视角，≥5 条意见，采纳 ≥2 条修正）
- [x] 复盘报告三件套归档成功（README / insight-extraction / actionable-items）
- [x] 复盘目录索引已更新

## 阶段 2：修复

- [x] 复盘发现的 P0/P1 缺陷已修复
- [x] 修复后构建链路未破坏（配置校验通过）

## 阶段 3：whl 打包验证

- [x] 新 wheel 已生成（`dist/xmnn-<version>-cp314-cp314-linux_x86_64.whl`）
- [x] wheel 内容完整（_libs、Nuitka .so、bootstrap、数据目录、relay/std、vta_hw/config）
- [x] 11 项验证全部通过

## 阶段 4：Docker 镜像

- [x] 生产级镜像构建成功（ubuntu:26.04 + Miniconda + Python 3.14 + xmnn wheel）
- [x] 镜像配置正确（北外/清华镜像源、时区 Asia/Shanghai、空 ENTRYPOINT）
- [x] 镜像内冒烟测试通过（import tvm/vta/xmnn + tvm.build）
- [x] 体积优化完成（缓存清理、无用依赖裁剪）
- [x] `docker save` 导出 tar 成功
- [x] `docker load` 还原验证通过

## 阶段 5：收尾

- [x] 相关文档已更新（BUILD_REPORT.md 等）
- [x] 修复变更已原子提交（Conventional Commits，中文描述）
- [x] 质量门通过记录与产出物清单已汇总