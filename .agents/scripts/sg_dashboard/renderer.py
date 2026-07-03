"""sg-dashboard HTML渲染模块。

将AggregateStats渲染为自包含HTML仪表盘，包含Mermaid图表和CSS样式。
"""

from __future__ import annotations

from datetime import datetime

from .charts import generate_mermaid_bar_chart, generate_mermaid_pie
from .constants import STAGE_NAMES, STAGE_ORDER
from .models import AggregateStats


def _build_top_reasons_rows(stats: AggregateStats) -> str:
    rows = ''
    for i, (reason, count) in enumerate(stats.top_intercept_reasons[:8], 1):
        rows += f'<tr><td>{i}</td><td><code>{reason}</code></td><td>{count}</td></tr>\n'
    return rows


def _build_session_rows(stats: AggregateStats) -> str:
    rows = ''
    for s in stats.sessions:
        stage_flow = ' → '.join(s.stages_entered) if s.stages_entered else '-'
        n_stages = len(set(s.stages_entered))
        intercept_pct = (s.operations_intercepted / s.operations_checked * 100) if s.operations_checked > 0 else 0
        status = '✅ 完成' if s.completed else ('⚠️ 进行中' if s.stages_entered else '❓ 无阶段')
        bypass_badge = f' 🔴{s.bypass_detected}' if s.bypass_detected > 0 else ''
        error_badge = f' 🟥{s.errors}' if s.errors > 0 else ''
        rows += f'''<tr>
            <td><code>{s.session_id}</code></td>
            <td>{status}{bypass_badge}{error_badge}</td>
            <td>{n_stages}</td>
            <td>{s.operations_checked}</td>
            <td class="warn">{s.operations_intercepted} ({intercept_pct:.0f}%)</td>
            <td>{s.jumps_approved}/{s.jumps_requested}</td>
            <td class="muted small">{stage_flow}</td>
        </tr>\n'''
    return rows


def _build_event_timeline(stats: AggregateStats) -> str:
    recent = []
    for s in stats.sessions:
        for e in s.events[-5:]:
            recent.append(e)
    recent = recent[-30:]
    timeline = ''
    for e in recent:
        level_cls = {'ERROR': 'ev-error', 'WARN': 'ev-warn', 'INFO': 'ev-info', 'DEBUG': 'ev-debug'}.get(e.level, '')
        timeline += f'''<div class="event {level_cls}">
            <span class="ev-level">{e.level}</span>
            <span class="ev-stage">{e.stage}</span>
            <span class="ev-role">{e.role}</span>
            <span class="ev-event">{e.event}</span>
            <span class="ev-msg">{e.msg[:80]}</span>
            <span class="ev-sid muted">{e.session}</span>
        </div>\n'''
    return timeline


def _build_stage_stats_rows(stats: AggregateStats) -> str:
    rows = ''
    for sid in sorted(set(list(stats.stage_entry_counts.keys()) + list(stats.stage_pass_counts.keys())),
                      key=lambda x: STAGE_ORDER.get(x, 99)):
        entries_n = stats.stage_entry_counts.get(sid, 0)
        passed = stats.stage_pass_counts.get(sid, 0)
        intercepted = stats.stage_intercept_counts.get(sid, 0)
        total_ops = passed + intercepted
        rate = f'{intercepted/total_ops*100:.0f}%' if total_ops > 0 else '-'
        rows += f'''<tr>
            <td><strong>{sid}</strong></td>
            <td>{STAGE_NAMES.get(sid, sid)}</td>
            <td>{entries_n}</td>
            <td>{passed}</td>
            <td class="{'warn' if intercepted > 0 else ''}">{intercepted}</td>
            <td>{rate}</td>
        </tr>\n'''
    return rows


def _build_jump_stats(stats: AggregateStats) -> str:
    skip_n = sum(1 for s in stats.sessions for jt, c in s.jump_types.items() if jt == 'skip' for _ in range(c))
    rollback_n = sum(1 for s in stats.sessions for jt, c in s.jump_types.items() if jt == 'rollback' for _ in range(c))
    return f'''<div class="stat-row">
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_requested}</div><div class="stat-label">跳转申请</div></div>
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_approved}</div><div class="stat-label">批准</div></div>
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_rejected}</div><div class="stat-label">拒绝</div></div>
        <div class="stat-card"><div class="stat-value">{skip_n}</div><div class="stat-label">正向跳过</div></div>
        <div class="stat-card"><div class="stat-value">{rollback_n}</div><div class="stat-label">逆向回退</div></div>
    </div>'''


def generate_html_dashboard(stats: AggregateStats, title: str = '阶段守卫日志仪表盘',
                            generated_from: str = '') -> str:
    """将聚合统计渲染为自包含HTML仪表盘。"""
    intercept_rate = f'{stats.interception_rate:.1f}%'
    approval_rate = f'{stats.approval_rate:.1f}%'
    completion_rate = f'{stats.completion_rate:.1f}%'

    event_pie = generate_mermaid_pie(stats.event_counts)
    stage_bar = generate_mermaid_bar_chart(stats.stage_intercept_counts, stats.stage_pass_counts)

    top_reasons_rows = _build_top_reasons_rows(stats)
    session_rows = _build_session_rows(stats)
    event_timeline = _build_event_timeline(stats)
    stage_stats_rows = _build_stage_stats_rows(stats)
    jump_stats = _build_jump_stats(stats)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --green: #4ade80; --yellow: #facc15; --red: #f87171; --orange: #fb923c;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: var(--bg); color: var(--text); padding: 24px; line-height:1.6; }}
h1 {{ font-size:1.8rem; margin-bottom:4px; }}
.subtitle {{ color:var(--muted); font-size:0.9rem; margin-bottom:24px; }}
.dashboard-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
.stat-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
             padding:20px; text-align:center; }}
.stat-value {{ font-size:2rem; font-weight:700; color:var(--accent); }}
.stat-label {{ color:var(--muted); font-size:0.85rem; margin-top:4px; }}
.stat-row {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:24px; }}
.stat-row .stat-card {{ flex:1; min-width:120px; }}
.section {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
           padding:20px; margin-bottom:20px; }}
.section h2 {{ font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; gap:8px; }}
.charts-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px; }}
@media (max-width:900px) {{ .charts-grid {{ grid-template-columns:1fr; }} }}
.mermaid {{ background:var(--bg); border-radius:8px; padding:16px; display:flex; justify-content:center; }}
table {{ width:100%; border-collapse:collapse; font-size:0.9rem; }}
th {{ text-align:left; padding:10px 8px; border-bottom:2px solid var(--border); color:var(--muted); font-weight:600; }}
td {{ padding:8px; border-bottom:1px solid var(--border); }}
tr:hover {{ background:rgba(56,189,248,0.05); }}
.warn {{ color:var(--yellow); }} .err {{ color:var(--red); }} .ok {{ color:var(--green); }}
.muted {{ color:var(--muted); }} .small {{ font-size:0.8rem; }}
.event {{ display:flex; gap:10px; align-items:center; padding:6px 10px; border-left:3px solid var(--border);
         margin-bottom:4px; font-size:0.82rem; font-family:'SF Mono',Consolas,monospace; }}
.ev-error {{ border-left-color:var(--red); background:rgba(248,113,113,0.08); }}
.ev-warn {{ border-left-color:var(--yellow); background:rgba(250,204,21,0.05); }}
.ev-info {{ border-left-color:var(--accent); }}
.ev-debug {{ border-left-color:var(--border); opacity:0.7; }}
.ev-level {{ font-weight:700; min-width:45px; font-size:0.75rem;
            padding:1px 6px; border-radius:4px; text-align:center; }}
.ev-error .ev-level {{ background:var(--red); color:#000; }}
.ev-warn .ev-level {{ background:var(--yellow); color:#000; }}
.ev-info .ev-level {{ background:var(--accent); color:#000; }}
.ev-debug .ev-level {{ background:var(--border); color:var(--muted); }}
.ev-stage {{ font-weight:600; color:var(--accent); min-width:32px; }}
.ev-role {{ color:var(--orange); min-width:80px; }}
.ev-event {{ color:var(--green); min-width:120px; }}
.ev-msg {{ flex:1; color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.ev-sid {{ color:var(--muted); font-size:0.75rem; }}
code {{ background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; font-size:0.85rem; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
.badge-green {{ background:rgba(74,222,128,0.15); color:var(--green); }}
.badge-yellow {{ background:rgba(250,204,21,0.15); color:var(--yellow); }}
.badge-red {{ background:rgba(248,113,113,0.15); color:var(--red); }}
.footer {{ text-align:center; color:var(--muted); font-size:0.8rem; margin-top:32px; padding-top:16px; border-top:1px solid var(--border); }}
</style>
</head>
<body>

<h1>🛡️ {title}</h1>
<div class="subtitle">
    生成时间: {now} | 数据来源: {generated_from} |
    <span class="badge badge-green">{stats.total_sessions} 个会话</span>
    <span class="badge badge-yellow">{stats.total_intercepted} 次拦截</span>
    <span class="badge badge-red">{stats.total_bypasses + stats.total_errors} 次异常</span>
</div>

<div class="dashboard-grid">
    <div class="stat-card">
        <div class="stat-value">{stats.total_sessions}</div>
        <div class="stat-label">会话总数</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{stats.total_entries}</div>
        <div class="stat-label">日志条目</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--yellow)">{intercept_rate}</div>
        <div class="stat-label">拦截率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--green)">{approval_rate}</div>
        <div class="stat-label">审批通过率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--green)">{completion_rate}</div>
        <div class="stat-label">完成率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--red)">{stats.total_bypasses}</div>
        <div class="stat-label">绕过检测</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--red)">{stats.total_errors}</div>
        <div class="stat-label">ERROR事件</div>
    </div>
</div>

{jump_stats}

<div class="charts-grid">
    <div class="section">
        <h2>📊 事件类型分布</h2>
        <div class="mermaid">
{event_pie}
        </div>
    </div>
    <div class="section">
        <h2>📈 各阶段操作拦截/放行对比</h2>
        <div class="mermaid">
{stage_bar}
        </div>
    </div>
</div>

<div class="section">
    <h2>🏆 高频拦截原因 Top-{len(stats.top_intercept_reasons[:8])}</h2>
    <table>
        <thead><tr><th>#</th><th>违规操作</th><th>拦截次数</th></tr></thead>
        <tbody>
{top_reasons_rows if top_reasons_rows else '<tr><td colspan="3" class="muted">无拦截记录</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>📋 各阶段统计</h2>
    <table>
        <thead><tr><th>阶段</th><th>名称</th><th>进入次数</th><th>放行操作</th><th>拦截操作</th><th>拦截率</th></tr></thead>
        <tbody>
{stage_stats_rows if stage_stats_rows else '<tr><td colspan="6" class="muted">无数据</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>🗂️ 会话详情</h2>
    <table>
        <thead><tr><th>会话ID</th><th>状态</th><th>阶段数</th><th>检查操作</th><th>拦截</th><th>审批(批/请)</th><th>阶段流转</th></tr></thead>
        <tbody>
{session_rows if session_rows else '<tr><td colspan="7" class="muted">无会话数据</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>⏱️ 最近事件时间线</h2>
{event_timeline if event_timeline else '<div class="muted">无事件数据</div>'}
</div>

<div class="footer">
    🛡️ SpecWeave 阶段守卫日志聚合仪表盘 |
    <a href="https://specweave.dev" style="color:var(--accent)">SpecWeave</a> |
    由 generate-sg-dashboard.py 生成
</div>

<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'dark',
    themeVariables: {{
        primaryColor: '#1e3a5f',
        primaryTextColor: '#e2e8f0',
        primaryBorderColor: '#38bdf8',
        lineColor: '#94a3b8',
        secondaryColor: '#1e293b',
        tertiaryColor: '#0f172a',
        fontFamily: 'inherit',
    }},
    pie: {{ useWidth: 400 }},
    xyChart: {{ width: 420, height: 300, plotReservedSpacePercent: 45 }},
}});
</script>
</body>
</html>'''
    return html
