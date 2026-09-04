# test-assets 说明

> 本目录为功能性测试资产目录（shell 脚本以绝对路径 `-v` 挂载 Docker volume，多个 py 脚本硬编码读取 `models/`）。

## 2026-09-04 C-4 大文件治理变更

- `visualization.html`（1,015 KB）已归档至 [caffe-comprehensive-comparison-charts.html](../../../../../docs/retrospective/reports/code-optimization/caffe-comprehensive-comparison-charts.html)（自包含 HTML，echarts 已内联）。
- `echarts.min.js`（1,009 KB）已删除：echarts@5 公共库，`gen_visualization.py` 内建 CDN 回退；重跑生成时如需本地化会重新下载。
- 上述两文件加入 `.gitignore`，防止再生成物回流 spec 目录。

<!-- source: .trae/specs/caffe-framework/caffe-comprehensive-comparison-test/test-assets/ -->
