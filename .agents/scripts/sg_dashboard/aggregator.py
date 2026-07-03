"""sg-dashboard 统计聚合模块。

将LogEntry列表聚合为AggregateStats。
"""

from __future__ import annotations

from collections import Counter

from .models import AggregateStats, LogEntry, SessionStats


def aggregate_entries(entries: list[LogEntry]) -> AggregateStats:
    """将日志条目列表聚合为全局统计。"""
    stats = AggregateStats()
    sessions: dict[str, SessionStats] = {}

    for entry in entries:
        stats.total_entries += 1
        if entry.prefix == 'SG-LOG':
            stats.total_sg_entries += 1
        else:
            stats.total_pdr_entries += 1
        stats.event_counts[entry.event] += 1
        stats.level_counts[entry.level] += 1

        sid = entry.session
        if sid not in sessions:
            sessions[sid] = SessionStats(session_id=sid, source_file=entry.source_file)
        s = sessions[sid]
        s.events.append(entry)
        s.roles_seen.add(entry.role)

        if entry.event == 'STAGE_ENTER':
            s.stages_entered.append(entry.stage)
            stats.stage_entry_counts[entry.stage] += 1
        elif entry.event == 'STAGE_EXIT':
            s.stages_exited.append(entry.stage)
            if entry.stage == 'S8':
                s.completed = True
        elif entry.event == 'BOUNDARY_CHECK':
            s.operations_checked += 1
            stats.total_operations_checked += 1
        elif entry.event == 'BOUNDARY_PASS':
            s.operations_passed += 1
            stats.total_passed += 1
            stats.stage_pass_counts[entry.stage] += 1
        elif entry.event == 'INTERCEPT':
            s.operations_intercepted += 1
            stats.total_intercepted += 1
            stats.stage_intercept_counts[entry.stage] += 1
            stats.role_intercept_counts[entry.role] += 1
            reason = entry.ctx.get('violating_operation', entry.ctx.get('detail', entry.msg))
            s.intercept_reasons[reason] += 1
        elif entry.event == 'BYPASS_DETECTED':
            s.bypass_detected += 1
            stats.total_bypasses += 1
        elif entry.event == 'ERROR':
            s.errors += 1
            stats.total_errors += 1
        elif entry.event == 'JUMP_REQUEST':
            jt = entry.ctx.get('jump_type', 'unknown')
            s.jumps_requested += 1
            s.jump_types[jt] += 1
            stats.total_jumps_requested += 1
        elif entry.event == 'JUMP_APPROVED':
            s.jumps_approved += 1
            stats.total_jumps_approved += 1
        elif entry.event == 'JUMP_REJECTED':
            s.jumps_rejected += 1
            stats.total_jumps_rejected += 1

    all_reasons = Counter()
    for s in sessions.values():
        all_reasons.update(s.intercept_reasons)
        if s.completed:
            stats.sessions_completed += 1

    stats.total_sessions = len(sessions)
    stats.top_intercept_reasons = all_reasons.most_common(10)
    stats.sessions = sorted(sessions.values(), key=lambda x: x.session_id)
    return stats
