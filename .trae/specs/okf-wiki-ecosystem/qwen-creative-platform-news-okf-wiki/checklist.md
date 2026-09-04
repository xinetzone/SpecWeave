# Checklist：资讯速报骨架验证

## 骨架完整性
- [x] index.md 存在且frontmatter含okf_version/type:bundle
- [x] concepts/ 仅1篇概念文档 + index
- [x] references/ 含article-source.md + verification.md + index
- [x] log.md 存在
- [x] 无examples/目录（资讯速报）

## 资讯速报特性
- [x] stale_after 设为2026-10-31（约2个月）
- [x] index.md性质声明标注"资讯速报"
- [x] 概念文档聚焦单一事件（多Agent剧组协同）

## 事实与核验
- [x] F-001~F-039全部登记（39条，无跳号）
- [x] P0核验8项，5✅3⚠️
- [x] 勘误1：Wan上一代为Wan 2.7非2.5（F-039）
- [x] 勘误2：Arena排名有时效性（F-038）
- [x] 勘误3：小云雀仅S2工具之一（F-036）
- [x] ManClaw搭载字节Seedance 2.0标注（F-035）
- [x] 导演观点F-031~F-034明确标注为作者观点

## 索引
- [x] ai-agent/index.md toctree追加qwen-creative-platform-news/index
- [x] ai-agent/index.md total_bundles 21→22
- [x] bundles/index.md total_bundles 270→271
- [x] bundles/index.md ai域 97→98

## 质量
- [x] 全部相对路径，无file:///实际链接
- [x] UTF-8编码（7文件全部通过）
- [x] toctree三级完整
- [x] external/无变更
- [x] 全部.md相对链接可达
