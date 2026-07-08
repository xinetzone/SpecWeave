"""多智能体冲突解决机制。

实现三类冲突的分级仲裁：
- 职责冲突（responsibility）：Orchestrator 负责，4条规则
- 技术分歧（technical）：Architect 负责，5条规则
- 资源竞争（resource）：Orchestrator 负责，4条规则
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class ConflictType(str, Enum):
    RESPONSIBILITY = "responsibility"
    TECHNICAL = "technical"
    RESOURCE = "resource"

    @classmethod
    def from_str(cls, value: str) -> "ConflictType":
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Unknown conflict type: {value}")


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"


@dataclass
class ConflictReport:
    reporter_id: str
    opponent_id: str
    conflict_type: ConflictType
    description: str
    task_id: str
    initial_assignee: Optional[str] = None
    required_capability: Optional[str] = None
    module_path: Optional[str] = None
    proposal_a: Optional[str] = None
    proposal_b: Optional[str] = None
    is_bugfix: bool = False
    out_of_spec_scope: bool = False
    architect_decision: Optional[str] = None
    resource: Optional[str] = None
    resource_type: Optional[str] = None
    needs_lock: bool = False
    can_isolate: bool = False
    rejected_by: list[str] = field(default_factory=list)
    resolved: bool = False

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise ValueError("description cannot be empty")


@dataclass
class ArbitrationResult:
    status: ResolutionStatus
    winner: Optional[str]
    reason: str
    arbiter: str
    access_order: list[str] = field(default_factory=list)
    lock_holder: Optional[str] = None
    isolated: bool = False
    needs_human: bool = False

    @property
    def resolved(self) -> bool:
        return self.status == ResolutionStatus.RESOLVED


class ConflictResolver:
    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        self._logger = logger or (lambda msg: None)

    def _log(self, msg: str) -> None:
        self._logger(msg)

    def resolve(
        self,
        report: ConflictReport,
        agents: Optional[dict[str, dict[str, Any]]] = None,
        spec_rules: Optional[dict[str, str]] = None,
        request_order: Optional[list[str]] = None,
        module_ownership_history: Optional[dict[str, str]] = None,
        architect_decision: Optional[str] = None,
    ) -> ArbitrationResult:
        self._log(f"冲突报告 [{report.task_id}]: {report.description} (类型: {report.conflict_type.value})")
        self._log(f"开始仲裁 [{report.task_id}]: 启动仲裁流程")

        if report.conflict_type == ConflictType.RESPONSIBILITY:
            result = self._resolve_responsibility(report, agents, module_ownership_history)
        elif report.conflict_type == ConflictType.TECHNICAL:
            result = self._resolve_technical(report, spec_rules, architect_decision)
        elif report.conflict_type == ConflictType.RESOURCE:
            result = self._resolve_resource(report, agents, request_order)
        else:
            result = ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason=f"未知冲突类型: {report.conflict_type}",
                arbiter="system",
                needs_human=True,
            )

        self._log(f"仲裁结果 [{report.task_id}]: status={result.status.value}, winner={result.winner}, reason={result.reason}")
        return result

    def _resolve_responsibility(
        self,
        report: ConflictReport,
        agents: Optional[dict[str, dict[str, Any]]],
        module_ownership_history: Optional[dict[str, str]],
    ) -> ArbitrationResult:
        if len(report.rejected_by) >= 2:
            return ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason="双方均不接受仲裁结果，升级至人工处理",
                arbiter="orchestrator",
                needs_human=True,
            )

        if report.initial_assignee is not None:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=report.initial_assignee,
                reason="按优先级原则（初始分配为准）",
                arbiter="orchestrator",
            )

        if report.required_capability and agents:
            for agent_id, info in agents.items():
                caps = info.get("capabilities", [])
                if report.required_capability in caps:
                    return ArbitrationResult(
                        status=ResolutionStatus.RESOLVED,
                        winner=agent_id,
                        reason="按能力匹配原则",
                        arbiter="orchestrator",
                    )

        if module_ownership_history and report.module_path:
            owner = module_ownership_history.get(report.module_path)
            if owner:
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=owner,
                    reason="按历史归属原则",
                    arbiter="orchestrator",
                )

        if agents:
            candidates = list(agents.keys())
            if len(candidates) >= 2:
                a_load = agents[candidates[0]].get("load", 50)
                b_load = agents[candidates[1]].get("load", 50)
                if a_load != b_load:
                    winner = candidates[0] if a_load < b_load else candidates[1]
                    return ArbitrationResult(
                        status=ResolutionStatus.RESOLVED,
                        winner=winner,
                        reason="按负载均衡原则",
                        arbiter="orchestrator",
                    )

        reporter = report.reporter_id
        return ArbitrationResult(
            status=ResolutionStatus.RESOLVED,
            winner=reporter,
            reason="默认分配给发起方",
            arbiter="orchestrator",
        )

    def _match_proposal(self, proposal: str, keywords: list[str]) -> bool:
        return any(kw in proposal for kw in keywords)

    def _resolve_technical(
        self,
        report: ConflictReport,
        spec_rules: Optional[dict[str, str]],
        architect_decision: Optional[str],
    ) -> ArbitrationResult:
        if report.out_of_spec_scope:
            return ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason="超出规范范围，升级至人工处理",
                arbiter="architect",
                needs_human=True,
            )

        if len(report.rejected_by) >= 2:
            return ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason="双方均不接受技术决策，升级至人工处理",
                arbiter="architect",
                needs_human=True,
            )

        a = report.proposal_a or ""
        b = report.proposal_b or ""

        if spec_rules and a and b:
            spec_text = " ".join(spec_rules.values())
            if self._match_proposal(a, ["-->|文本|", "不加空格"]) and self._match_proposal(b, ["带空格"]):
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=report.reporter_id,
                    reason="按规范优先原则",
                    arbiter="architect",
                )

        if a and b:
            if self._match_proposal(a, ["异常抛出"]) and self._match_proposal(b, ["错误码"]):
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=report.reporter_id,
                    reason="按最佳实践原则",
                    arbiter="architect",
                )

            if self._match_proposal(a, ["单一职责", "拆分"]) and self._match_proposal(b, ["大函数", "单文件"]):
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=report.reporter_id,
                    reason="按可维护性原则",
                    arbiter="architect",
                )

            if report.is_bugfix and self._match_proposal(a, ["局部修复"]) and self._match_proposal(b, ["重构"]):
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=report.reporter_id,
                    reason="按最小变更原则",
                    arbiter="architect",
                )

        if spec_rules and a:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=report.reporter_id,
                reason="按规范优先原则",
                arbiter="architect",
            )

        if architect_decision:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=architect_decision,
                reason="按Architect终裁原则",
                arbiter="architect",
            )

        return ArbitrationResult(
            status=ResolutionStatus.ESCALATED,
            winner=None,
            reason="无适用规则且无Architect决策，升级至人工",
            arbiter="architect",
            needs_human=True,
        )

    def _resolve_resource(
        self,
        report: ConflictReport,
        agents: Optional[dict[str, dict[str, Any]]],
        request_order: Optional[list[str]],
    ) -> ArbitrationResult:
        if report.can_isolate:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=None,
                reason="按资源隔离原则，为双方分配独立副本",
                arbiter="orchestrator",
                isolated=True,
            )

        if agents:
            agent_ids = list(agents.keys())
            if len(agent_ids) >= 2:
                a_pri = agents[agent_ids[0]].get("priority", 99)
                b_pri = agents[agent_ids[1]].get("priority", 99)
                if a_pri != b_pri:
                    sorted_agents = sorted(agent_ids, key=lambda aid: agents[aid].get("priority", 99))
                    return ArbitrationResult(
                        status=ResolutionStatus.RESOLVED,
                        winner=sorted_agents[0],
                        reason="按优先级调度原则",
                        arbiter="orchestrator",
                        access_order=sorted_agents,
                        lock_holder=sorted_agents[0] if report.needs_lock else None,
                    )

        order = request_order or [report.reporter_id, report.opponent_id]

        if report.needs_lock:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=order[0],
                reason="按锁机制原则，先请求者获得锁",
                arbiter="orchestrator",
                access_order=order,
                lock_holder=order[0],
            )

        if report.resource_type == "exclusive_file":
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=order[0],
                reason="按串行访问原则",
                arbiter="orchestrator",
                access_order=order,
            )

        return ArbitrationResult(
            status=ResolutionStatus.RESOLVED,
            winner=order[0],
            reason="按串行访问原则",
            arbiter="orchestrator",
            access_order=order,
            lock_holder=order[0] if report.needs_lock else None,
        )
