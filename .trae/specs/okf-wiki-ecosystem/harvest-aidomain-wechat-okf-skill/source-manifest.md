# Source Manifest

## Account

- `account_name`: 爱域研究社
- `scope`: 公开可检索文章
- `verification_time`: 2026-09-24
- `stopping_rules`: 不绕过登录、验证码、邀请码或访问控制；连续访问失败的条目标记为 `not-collected`

## Public Sources

| ID | URL | Title | Account | Published | Accessibility | Ownership evidence | Status |
|---|---|---|---|---|---|---|---|
| SRC-001 | https://mp.weixin.qq.com/s/8IqLqZ8uIAhhpv9xvFqmBA | 手把手教你追女生：拿捏情绪惯性，让女生慢慢产生依赖感 | 爱域研究社 | 2026-09-23 13:21 | 公开可访问，无需登录/验证码 | `#activity-name`、`#js_name`、`author`、`og:article:author` 均显示“爱域研究社”；`og:url` 与 source URL 一致 | `verified` |

## Collection Notes

- 本 manifest 只登记最小必要元数据，不保存文章全文。
- `SRC-001` 的主题初判为恋爱关系与情感建议；具体事实、作者观点和执行者洞察将在 R 阶段分层登记。
- 页面未发现 `rel="canonical"`；使用 Open Graph `og:url` 作为页面归属定位。
- 尚未发现的文章不等同于不存在；“全部”仅指在执行时点和公开入口下成功发现并核验的集合。

## Not Collected

| Candidate | Reason | Retry policy |
|---|---|---|
| None | 当前已提供且核验的 URL 可公开访问 | 若后续入口触发登录墙、验证码或连续失败，直接记录原因并停止绕过式重试 |
