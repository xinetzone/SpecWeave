# Docker 镜像导出归档 - Verification Checklist

## 前置检查
- [ ] Docker 服务运行中，`docker info` 正常返回
- [ ] 镜像 `caffe-cpu:standalone-jupyter-test` 存在（ID: 3998b17e0696）
- [ ] 目标目录 `D:\BaiduSyncdisk\docker\` 存在且可写
- [ ] D 盘可用空间 >5GB

## 导出执行
- [ ] `docker save` 命令执行完成，退出码为 0
- [ ] 生成文件名为 `caffe-cpu-standalone-jupyter_20260727.tar`
- [ ] 文件位于 `D:\BaiduSyncdisk\docker\` 目录

## 完整性验证
- [ ] 文件大小 >1GB（预期 2GB 左右）
- [ ] tar 文件可读（`tar -tf` 无错误）
- [ ] tar 内包含 `manifest.json`（Docker 镜像格式标志）
- [ ] tar 内包含 layer 目录和 json 配置文件

## 结果交付
- [ ] 输出文件绝对路径供用户确认
- [ ] 输出文件大小（人类可读格式）
- [ ] 输出 `docker load` 加载命令供后续使用
