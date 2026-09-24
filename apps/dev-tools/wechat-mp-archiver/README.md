# wechat-mp-archiver

微信公众号全量内容归档工具：通过**私有部署的开源采集服务**（R2 主路线）获取指定公众号的历史文章列表，由本 Python 管线完成正文/富媒体下载、元数据管理、断点续采与增量更新，产出三种形态：

- **离线归档**：原始 HTML 快照 + 本地化图片 + Markdown，按 `archive/<账号>/<年>/<日期_标题>/` 组织；
- **RAG 语料**：带 YAML frontmatter 的 Markdown 导出（Task 10）；
- **分析报表**：更新趋势、失败/对账清单（Task 11）。

技术选型与合规边界见 [技术方案文档](../../../docs/knowledge/operations/wechat-mp-full-archive-solution.md)。
仅供个人学习研究使用，请勿公开再分发归档内容。

## 安装

```bash
cd apps/dev-tools/wechat-mp-archiver
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 采集服务部署（首次使用必做）

采集服务通过 Docker Compose 私有部署（仅绑定回环地址），扫码登录由账号管理员本人完成，步骤与登录态失效续期见 [deploy/README.md](deploy/README.md)。

## 配置

```bash
copy .env.example .env   # PowerShell；bash: cp .env.example .env
```

`.env` 中至少确认：归档根目录、数据库路径、限速参数；采集服务地址（默认 `http://127.0.0.1:5000`）在采集服务私有部署并扫码后生效。**凭证只走环境变量/.env，`.env` 已被 gitignore。**

## 命令

```bash
mp-archiver doctor     # 环境自检（数据库、归档目录、采集服务连通性）
mp-archiver init-db    # 初始化 SQLite 元数据库
mp-archiver list -a 意识食谱          # 同步指定公众号全量文章列表
mp-archiver list -a 意识食谱 --max-pages 2   # 调试：仅翻 2 页（不做下架对账）
mp-archiver fetch -a 意识食谱         # 归档正文（HTML/Markdown/图片/metadata 四件套）
mp-archiver fetch -a 意识食谱 --limit 10     # 先小批量试跑
mp-archiver fetch -a 意识食谱 --include-failed  # 同时重试此前失败的文章
mp-archiver sync-official -a 意识食谱  # 可选：自有认证号官方清单交叉补全（见 deploy/README.md 第 11 节）
pytest                 # 运行测试
```

`list` 会自动发现采集服务的搜索/历史端点（可由环境变量覆写），翻页采集元数据并幂等入库；完整翻到尾页后执行下架/不可见文章对账，凭证失效时返回退出码 2 并提示重新扫码。

`fetch` 直连 `mp.weixin.qq.com` 逐篇下载：正文图片（含微信懒加载 `data-src`）全部本地化并改写为相对路径，单图失败保留远程引用并登记进 `metadata.json`；平台明确删除/违规的文章标记 skipped，风控页与传输错误标记 failed 且不影响后续文章。归档产物位于 `archive/<账号>/<YYYY>/<YYYY-MM-DD_标题>/`。

## 结构

```
src/mp_archiver/
├── config.py          # pydantic-settings 配置（MP_ARCHIVER_ 前缀）
├── models.py          # 采集状态枚举与文章模型
├── logging_utils.py   # 凭证脱敏日志
├── naming.py          # 跨平台安全文件名
├── http_client.py     # 保守限速 + 指数退避 HTTP 客户端
├── db/                # SQLite 五表（articles/media/comments/metrics/sync_state）
├── adapters/          # 采集源适配器（Task 3+）
├── core/              # 归档管线（Task 4+）
└── exporters/         # RAG/报表导出（Task 10+）
```
