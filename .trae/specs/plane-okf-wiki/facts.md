# Plane 博文事实登记（spec 侧 · 双份登记之一）

> 编号区间 F-001 ~ F-057。与 `projects/awesome-okf-xs/doc/bundles/jishu/dev/plane/references/article-source.md` 逐号对应。
> 级别：P0 必核验 / P1 选核验 / P2 可单源。**作者观点**显式标注。

| 编号 | 事实摘要 | 级别 |
|------|---------|------|
| F-001 | Plane 定位为 Jira、Linear、Monday、ClickUp 的开源替代 | P0 |
| F-002 | 仓库 Star 约 6.0 万（标题「6.0 万 Star」） | P0 |
| F-003 | 仓库地址 https://github.com/makeplane/plane | P0 |
| F-004 | 建库时间 2022 年 11 月 | P0 |
| F-005 | 自托管拆成三套各自独立的代码库：Community / Commercial / Airgapped | P0 |
| F-006 | Community 开源免费、人数不封顶、功能对齐云端免费档、代码可自审自改 | P0 |
| F-007 | Commercial 闭源、功能与云端完全拉平、内置免费档每工作区送 12 个座席 | P0 |
| F-008 | Airgapped 把商用版改成完全离线，更新从自己的镜像仓库拉 | P0 |
| F-009 | 三套发版节奏分开：新功能先云端 → 再商用 → 最后社区 | P0 |
| F-010 | 三套之间无强制迁移；社区版无隐藏限制代码 | P0 |
| F-011 | 离线版只随最高一档企业方案提供，需走商务渠道 | P1 |
| F-012 | 社区版项目/任务/成员均不封顶，REST API 与 Webhook 开放 | P0 |
| F-013 | 技术栈：后端 Django、前端 React，前后端同仓 | P0 |
| F-014 | 自托管路径有 Docker Compose 与 Kubernetes 两条 | P0 |
| F-015 | 最小工作单位 Work Item：富文本、附件、子任务、关联、负责人、标签、优先级 | P0 |
| F-016 | 编辑器认 Markdown，代码块与图片可直接贴，评论可 @ 同事 | P1 |
| F-017 | 状态列可自定义，默认 Todo / In Progress / Done 三档 | P1 |
| F-018 | Cycles 对应 Scrum Sprint，燃尽图与完成率自动计算 | P0 |
| F-019 | 周期收尾未完成任务可直接转到下一期 | P1 |
| F-020 | Modules 管跨周期工作（如横跨三四个周期的版本重构） | P0 |
| F-021 | 模块自带进度条与状态分布 | P1 |
| F-022 | 同一批任务五种版式：看板/列表/日历/甘特图/表格，底层同一份数据 | P0 |
| F-023 | 筛选条件配好可存成视图并分享给团队其他人 | P1 |
| F-024 | 五种版式在免费档全部开放 | P0 |
| F-025 | Intake：外部人员无需注册，通过表单提需求/bug，先进待审队列 | P1 |
| F-026 | 官方集成：GitHub、GitLab、Slack、Sentry | P0 |
| F-027 | 代码合并能带着任务状态一起变 | P1 |
| F-028 | Slack 里可直接开任务 | P1 |
| F-029 | AI 可问进度/整理描述；自部署实例挂自己的模型 Key，请求不出本机 | P1 |
| F-030 | 内置文档：富文本、可嵌图片/视频/Figma，写完可一键转成任务 | P1 |
| F-031 | 项目层面有 Pages，工作区层面有 Wiki | P1 |
| F-032 | 统计为跨项目实时面板，按负责人/状态/优先级摊开，带趋势图 | P1 |
| F-033 | 社区版一键脚本：mkdir → cd → curl setup.sh → chmod +x → ./setup.sh | P0 |
| F-034 | 脚本菜单八项：Install(arm64)/Start/Stop/Restart/Upgrade/View Logs/Backup Data/Exit | P0 |
| F-035 | 选 Install 建出 plane-app 目录，拉下 compose 与 environment 文件 | P0 |
| F-036 | 四个关键环境键：HTTP/HTTPS 端口默认 80/443；WEB_URL 与 CORS_ALLOWED_ORIGINS 默认本机 | P0 |
| F-037 | 商用版一行管道命令安装，再用 sudo prime-cli 配数据库与存储 | P1 |
| F-038 | 机器门槛 2 核 4G 可跑 | P0 |
| F-039 | 单容器版十来分钟可起，官方称只适合体验、勿上生产 | P1 |
| F-040 | 生产环境建议把数据库与对象存储挪到容器外 | P0 |
| F-041 | 容器内置 Postgres 15.5、Redis 7.2.4 与 MinIO | P0 |
| F-042 | prime-cli configure 可改：代理监听端口、单文件上限（默认 5 MB）、外部 Postgres/Redis、对象存储 | P1 |
| F-043 | 对象存储只认 S3 兼容；地址不能填本机；密码勿含特殊字符（否则预签名上传失败） | P1 |
| F-044 | Kubernetes 官方提供 Helm Chart，用 PLANE_VERSION 指定版本号 | P1 |
| F-045 | 官方明说不要写 stable，必须写具体版本号 | P1 |
| F-046 | 快速安装把 Postgres/Redis/MinIO 起成有状态服务，配 longhorn 存储类与 nginx 入口 | P1 |
| F-047 | 一个实例可放多个工作区；管理员专属路径叫 God mode | P0 |
| F-048 | God mode 管实例名与 ID、匿名遥测、SMTP、SSO 与 OAuth、免邀请注册、能否建工作区 | P1 |
| F-049 | SMTP 需早配，否则邀请邮件发不出去 | P2 |
| F-050 | 单点登录、审计日志等属商用版付费档，按座席收费 | P1 |
| F-051 | 许可证 AGPL 3.0：二次开发再商用有影响，团队内部自用不受限 | P0 |
| F-052 | **元事实**：作者明示未实际部署过 Plane，功能与部署描述来自官方 README/开发者文档与来源正文 | — |
| F-053 | **作者观点**：Redmine、OpenProject 活了十几年、功能不缺但界面停留在上一个时代 | P2 |
| F-054 | **作者观点**：Jira 配置成本高；Linear 闭源、按人头计费不便宜 | P2 |
| F-055 | **作者观点**：适合中小研发团队/在意数据归属团队/预算紧张初创团队/市场运营等非技术团队 | P2 |
| F-056 | **补充事实**（源文未提）：官方 Compose 还内置 RabbitMQ 作为后台任务消息队列 | P1 |
| F-057 | **补充事实**（源文未提）：2026-10-08 上游 commit 将 MinIO 镜像切至 pgsty/silo | P1 |
