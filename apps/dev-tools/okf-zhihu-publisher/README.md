# OKF Zhihu Publisher

将 OKF 知识包（bundles）批量发布到知乎知识库的命令行工具，支持增量同步。

## 特性

- **增量同步**：基于内容哈希，只上传变化的文件
- **结构化元数据**：文件名嵌入层级路径，提升检索召回质量
- **额度感知**：自动读取剩余额度，超额自动暂停
- **断点续传**：失败后重跑从断点继续
- **Dry-run 预览**：先看将要执行的操作，不实际调用 API

## 架构

```
okf_zhihu_publisher/
├── __init__.py
├── __main__.py        # CLI 入口
├── cli.py             # 命令行参数解析
├── api_client.py      # 知乎知识库 API 适配层
├── state_manager.py   # 状态文件管理（publish-state.json）
├── bundle_scanner.py  # OKF bundle 扫描器
├── transformer.py     # 转换适配层（元数据增强）
├── publisher.py       # 发布编排层
└── config.py          # 配置管理
```

## 快速开始

```bash
# 配置 Access Secret
export ZHIHU_ACCESS_SECRET="your-secret-here"

# 预览同步操作（不实际上传）
python -m okf_zhihu_publisher sync --bundles-dir ../../projects/awesome-okf-xs/doc/bundles --dry-run

# 执行同步
python -m okf_zhihu_publisher sync --bundles-dir ../../projects/awesome-okf-xs/doc/bundles
```
