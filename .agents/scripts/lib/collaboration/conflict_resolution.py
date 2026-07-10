"""多智能体冲突解决机制。

实现三类冲突的分级仲裁：
- 职责冲突（responsibility）：Orchestrator 负责，4条规则
- 技术分歧（technical）：Architect 负责，5条规则
- 资源竞争（resource）：Orchestrator 负责，4条规则

设计保障：
- 无死锁：资源锁支持超时，拒绝列表自动去重，升级机制防止无限循环
- 无饥饿：能力匹配/负载均衡覆盖所有候选agent
- 并发安全：传入的可变参数做防御性拷贝，不修改调用方数据
- 可配置：技术分歧规则通过best_practice_rules配置，非硬编码
"""

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any, Optional
from collections.abc import Callable
from copy import deepcopy

_CONFLICT_TYPE_MAPPING: dict[str, "ConflictType"] = {}


class ConflictType(StrEnum):
    RESPONSIBILITY = "responsibility"
    TECHNICAL = "technical"
    RESOURCE = "resource"

    @classmethod
    def from_str(cls, value: str) -> "ConflictType":
        global _CONFLICT_TYPE_MAPPING
        if not _CONFLICT_TYPE_MAPPING:
            _CONFLICT_TYPE_MAPPING = {m.value: m for m in cls}
        try:
            return _CONFLICT_TYPE_MAPPING[value]
        except KeyError:
            raise ValueError(f"Unknown conflict type: {value}") from None


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"


DEFAULT_LOCK_TIMEOUT_SECONDS = 300

BEST_PRACTICE_KEYWORDS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "exception_over_error_code": (("异常抛出", "exception", "try"), ("错误码", "error code", "返回码")),
    "single_responsibility": (("单一职责", "拆分", "modular", "small function"), ("大函数", "单文件", "monolithic")),
    "minimal_change_bugfix": (("局部修复", "最小改动", "minimal change"), ("重构", "重写", "refactor", "rewrite")),
}


@dataclass
class ConflictReport:
    reporter_id: str
    opponent_id: str
    conflict_type: ConflictType
    description: str
    task_id: str
    initial_assignee: str | None = None
    required_capability: str | None = None
    module_path: str | None = None
    proposal_a: str | None = None
    proposal_b: str | None = None
    is_bugfix: bool = False
    out_of_spec_scope: bool = False
    architect_decision: str | None = None
    resource: str | None = None
    resource_type: str | None = None
    needs_lock: bool = False
    can_isolate: bool = False
    rejected_by: list[str] = field(default_factory=list)
    resolved: bool = False

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise ValueError("description cannot be empty")
        self.rejected_by = list(dict.fromkeys(self.rejected_by))

    def add_rejection(self, agent_id: str) -> None:
        if agent_id not in self.rejected_by:
            self.rejected_by.append(agent_id)


@dataclass
class ArbitrationResult:
    status: ResolutionStatus
    winner: str | None
    reason: str
    arbiter: str
    access_order: list[str] = field(default_factory=list)
    lock_holder: str | None = None
    lock_timeout_seconds: int | None = None
    isolated: bool = False
    needs_human: bool = False

    @property
    def resolved(self) -> bool:
        return self.status == ResolutionStatus.RESOLVED


class ConflictResolver:
    def __init__(
        self,
        logger: Callable[[str], None] | None = None,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
        best_practice_rules: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] | None = None,
    ):
        self._logger = logger or (lambda msg: None)
        self._lock_timeout = lock_timeout_seconds
        self._bp_rules = best_practice_rules or BEST_PRACTICE_KEYWORDS

    def _log(self, msg: str) -> None:
        self._logger(msg)

    @staticmethod
    def _diagnose_load(agent_info: dict[str, Any]) -> str:
        """诊断agent负载值问题，返回异常原因字符串；正常值返回空字符串。"""
        load = agent_info.get("load")
        if load is None:
            return "缺失(None)"
        if not isinstance(load, (int, float)):
            return f"类型异常({type(load).__name__}={load!r})"
        if isinstance(load, bool):
            return f"类型异常(bool={load})"
        if isinstance(load, float) and load != load:
            return f"非数值(NaN)"
        if load < 0:
            return f"负值({load})"
        if load > 100:
            return f"超范围({load}>100)"
        return ""

    def _log_load_validation(self, task_id: str, candidate_ids: list[str],
                             valid_ids: list[str], agents: dict[str, dict[str, Any]]) -> None:
        """输出负载校验详细日志，列出每个被过滤agent的异常原因。"""
        invalid_ids = [aid for aid in candidate_ids if aid not in valid_ids]
        if invalid_ids:
            details = [f"{aid}[{self._diagnose_load(agents[aid])}]" for aid in invalid_ids]
            self._log(
                f"[WARNING] 负载校验 [{task_id}]: 过滤{len(invalid_ids)}个负载异常agent: "
                f"{', '.join(details)}"
            )
        valid_loads = {aid: agents[aid]["load"] for aid in valid_ids}
        self._log(
            f"负载校验 [{task_id}]: 有效候选{len(valid_ids)}个, "
            f"负载分布: {valid_loads}"
        )

    def resolve(
        self,
        report: ConflictReport,
        agents: dict[str, dict[str, Any]] | None = None,
        spec_rules: dict[str, str] | None = None,
        request_order: list[str] | None = None,
        module_ownership_history: dict[str, str] | None = None,
        architect_decision: str | None = None,
    ) -> ArbitrationResult:
        agents_safe = deepcopy(agents) if agents is not None else None
        spec_safe = deepcopy(spec_rules) if spec_rules is not None else None
        order_safe = list(request_order) if request_order is not None else None
        history_safe = dict(module_ownership_history) if module_ownership_history is not None else None

        self._log(f"冲突报告 [{report.task_id}]: {report.description} (类型: {report.conflict_type.value})")
        self._log(f"开始仲裁 [{report.task_id}]: 启动仲裁流程")

        if len(report.rejected_by) >= 2:
            self._log(f"升级 [{report.task_id}]: 双方均拒绝 ({report.rejected_by})")
            arbiter_name = "orchestrator"
            if report.conflict_type == ConflictType.TECHNICAL:
                arbiter_name = "architect"
            return ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason="双方均不接受仲裁结果，升级至人工处理",
                arbiter=arbiter_name,
                needs_human=True,
            )

        if report.conflict_type == ConflictType.RESPONSIBILITY:
            result = self._resolve_responsibility(report, agents_safe, history_safe)
        elif report.conflict_type == ConflictType.TECHNICAL:
            result = self._resolve_technical(report, spec_safe, architect_decision)
        elif report.conflict_type == ConflictType.RESOURCE:
            result = self._resolve_resource(report, agents_safe, order_safe)
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
        agents: dict[str, dict[str, Any]] | None,
        module_ownership_history: dict[str, str] | None,
    ) -> ArbitrationResult:
        if report.initial_assignee is not None:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=report.initial_assignee,
                reason="按优先级原则（初始分配为准）",
                arbiter="orchestrator",
            )

        if report.required_capability:
            if not agents:
                self._log(f"升级 [{report.task_id}]: 指定了所需能力但无可用agents")
                return ArbitrationResult(
                    status=ResolutionStatus.ESCALATED,
                    winner=None,
                    reason=f"指定了所需能力 '{report.required_capability}' 但无可用agents，需人工分配",
                    arbiter="orchestrator",
                    needs_human=True,
                )
            candidates = [
                aid for aid, info in agents.items()
                if report.required_capability in info.get("capabilities", [])
            ]
            self._log(
                f"能力匹配 [{report.task_id}]: 需'{report.required_capability}'能力, "
                f"总agents={len(agents)}, 匹配候选={candidates}"
            )
            if len(candidates) == 0:
                self._log(f"升级 [{report.task_id}]: 无agent具备所需能力 '{report.required_capability}'")
                return ArbitrationResult(
                    status=ResolutionStatus.ESCALATED,
                    winner=None,
                    reason=f"无agent具备所需能力 '{report.required_capability}'，需人工分配具备能力的资源",
                    arbiter="orchestrator",
                    needs_human=True,
                )
            if len(candidates) == 1:
                winner_load = agents[candidates[0]].get("load", "未知")
                self._log(
                    f"仲裁 [{report.task_id}]: 唯一匹配候选={candidates[0]}(load={winner_load}), "
                    f"按能力匹配原则分配"
                )
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=candidates[0],
                    reason="按能力匹配原则",
                    arbiter="orchestrator",
                )
            if len(candidates) > 1:
                valid_load_candidates = [
                    aid for aid in candidates
                    if isinstance(agents[aid].get("load"), (int, float))
                    and not isinstance(agents[aid].get("load"), bool)
                    and 0 <= agents[aid]["load"] <= 100
                ]
                self._log_load_validation(report.task_id, candidates, valid_load_candidates, agents)
                if not valid_load_candidates:
                    diag_details = [f"{aid}[{self._diagnose_load(agents[aid])}]" for aid in candidates]
                    self._log(
                        f"[WARNING] 升级 [{report.task_id}]: 所有{len(candidates)}个候选agent负载值均异常: "
                        f"{', '.join(diag_details)}"
                    )
                    return ArbitrationResult(
                        status=ResolutionStatus.ESCALATED,
                        winner=None,
                        arbiter="orchestrator",
                        reason=f"无有效负载数据的候选agent（需{report.required_capability}能力），需人工分配",
                        needs_human=True,
                    )
                best = min(valid_load_candidates, key=lambda aid: agents[aid]["load"])
                best_load = agents[best]["load"]
                tie_count = sum(1 for aid in valid_load_candidates if agents[aid]["load"] == best_load)
                self._log(
                    f"负载均衡 [{report.task_id}]: 最低负载={best_load}, "
                    f"winner={best}(并列{tie_count}个), 按能力+负载均衡分配"
                )
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=best,
                    reason="按能力匹配+负载均衡原则（过滤异常负载值）",
                    arbiter="orchestrator",
                )

        if module_ownership_history and report.module_path:
            owner = module_ownership_history.get(report.module_path)
            if owner and (not agents or owner in agents):
                self._log(
                    f"历史归属 [{report.task_id}]: 模块{report.module_path}历史owner={owner}, "
                    f"按历史归属原则分配"
                )
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=owner,
                    reason="按历史归属原则",
                    arbiter="orchestrator",
                )

        if agents and len(agents) >= 2:
            self._log(f"全局负载均衡 [{report.task_id}]: 进入全局负载均衡路径, 总agents={len(agents)}")
            valid_agents = {
                aid: info for aid, info in agents.items()
                if isinstance(info.get("load"), (int, float))
                and not isinstance(info.get("load"), bool)
                and 0 <= info["load"] <= 100
            }
            agent_ids = list(agents.keys())
            valid_ids = list(valid_agents.keys())
            self._log_load_validation(report.task_id, agent_ids, valid_ids, agents)
            if not valid_agents:
                diag_details = [f"{aid}[{self._diagnose_load(info)}]" for aid, info in agents.items()]
                self._log(
                    f"[WARNING] 升级 [{report.task_id}]: 所有{len(agents)}个agent负载值均异常: "
                    f"{', '.join(diag_details)}"
                )
                return ArbitrationResult(
                    status=ResolutionStatus.ESCALATED,
                    winner=None,
                    arbiter="orchestrator",
                    reason="所有agent负载数据均异常，需人工分配",
                    needs_human=True,
                )
            loads = {aid: info["load"] for aid, info in valid_agents.items()}
            min_load = min(loads.values())
            best_candidates = [aid for aid, load in loads.items() if load == min_load]
            winner = best_candidates[0]
            self._log(
                f"负载均衡 [{report.task_id}]: 最低负载={min_load}, "
                f"winner={winner}(并列{len(best_candidates)}个, 全部并列: {best_candidates}), "
                f"按全局负载均衡分配"
            )
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=winner,
                reason="按负载均衡原则（过滤异常负载值）",
                arbiter="orchestrator",
            )

        reporter = report.reporter_id
        self._log(
            f"默认分配 [{report.task_id}]: agents不足2个({len(agents) if agents else 0}), "
            f"默认分配给发起方={reporter}"
        )
        return ArbitrationResult(
            status=ResolutionStatus.RESOLVED,
            winner=reporter,
            reason="默认分配给发起方",
            arbiter="orchestrator",
        )

    def _match_proposal(self, proposal: str, keywords: tuple[str, ...]) -> bool:
        pl = proposal.lower()
        return any(kw.lower() in pl for kw in keywords)

    @staticmethod
    def _substring_match_score(proposal: str, spec: str, ngram_size: int = 4) -> int:
        pl = proposal.lower().strip()
        sl = spec.lower()
        if not pl or not sl:
            return 0
        score = 0
        for i in range(len(pl) - ngram_size + 1):
            ngram = pl[i:i + ngram_size]
            if len(ngram.strip()) >= 2 and ngram in sl:
                score += 1
        if pl in sl:
            score += len(pl)
        return score

    def _count_best_practice_matches(self, proposal: str) -> int:
        if not proposal:
            return 0
        score = 0
        for positive_kws, negative_kws in self._bp_rules.values():
            if self._match_proposal(proposal, positive_kws):
                score += 1
            if self._match_proposal(proposal, negative_kws):
                score -= 1
        return score

    def _resolve_technical(
        self,
        report: ConflictReport,
        spec_rules: dict[str, str] | None,
        architect_decision: str | None,
    ) -> ArbitrationResult:
        if report.out_of_spec_scope:
            return ArbitrationResult(
                status=ResolutionStatus.ESCALATED,
                winner=None,
                reason="超出规范范围，升级至人工处理",
                arbiter="architect",
                needs_human=True,
            )

        a = report.proposal_a or ""
        b = report.proposal_b or ""

        if spec_rules and a and b:
            spec_text = " ".join(spec_rules.values())
            a_score = self._substring_match_score(a, spec_text)
            b_score = self._substring_match_score(b, spec_text)
            if a_score != b_score:
                winner = report.reporter_id if a_score > b_score else report.opponent_id
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=winner,
                    reason="按规范优先原则（匹配度更高）",
                    arbiter="architect",
                )

        if a and b:
            score_a = self._count_best_practice_matches(a)
            score_b = self._count_best_practice_matches(b)
            if score_a != score_b:
                winner = report.reporter_id if score_a > score_b else report.opponent_id
                if score_a > score_b and self._match_proposal(a, ("局部修复", "最小改动")) and report.is_bugfix:
                    reason = "按最小变更原则"
                elif self._match_proposal(a, ("异常抛出", "exception")) and self._match_proposal(b, ("错误码",)):
                    reason = "按最佳实践原则（异常优于错误码）"
                elif self._match_proposal(a, ("单一职责", "拆分")) and self._match_proposal(b, ("大函数", "单文件")):
                    reason = "按可维护性原则"
                else:
                    reason = "按最佳实践原则"
                return ArbitrationResult(
                    status=ResolutionStatus.RESOLVED,
                    winner=winner,
                    reason=reason,
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
        agents: dict[str, dict[str, Any]] | None,
        request_order: list[str] | None,
    ) -> ArbitrationResult:
        if report.can_isolate:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=None,
                reason="按资源隔离原则，为双方分配独立副本",
                arbiter="orchestrator",
                isolated=True,
            )

        order: list[str]
        if request_order:
            order = list(request_order)
        else:
            order = [report.reporter_id, report.opponent_id]

        if agents:
            prioritized = [aid for aid in order if aid in agents]
            if not prioritized:
                prioritized = list(agents.keys())
            if len(prioritized) >= 1:
                sorted_by_pri = sorted(
                    prioritized,
                    key=lambda aid: (agents[aid].get("priority", 99), order.index(aid) if aid in order else 999),
                )
                if len(sorted_by_pri) >= 2:
                    top_pri = agents[sorted_by_pri[0]].get("priority", 99)
                    second_pri = agents[sorted_by_pri[1]].get("priority", 99)
                    if top_pri != second_pri:
                        return ArbitrationResult(
                            status=ResolutionStatus.RESOLVED,
                            winner=sorted_by_pri[0],
                            reason="按优先级调度原则",
                            arbiter="orchestrator",
                            access_order=sorted_by_pri,
                            lock_holder=sorted_by_pri[0] if report.needs_lock else None,
                            lock_timeout_seconds=self._lock_timeout if report.needs_lock else None,
                        )

        if report.needs_lock:
            return ArbitrationResult(
                status=ResolutionStatus.RESOLVED,
                winner=order[0],
                reason=f"按锁机制原则，先请求者获得锁（超时{self._lock_timeout}秒）",
                arbiter="orchestrator",
                access_order=order,
                lock_holder=order[0],
                lock_timeout_seconds=self._lock_timeout,
            )

        return ArbitrationResult(
            status=ResolutionStatus.RESOLVED,
            winner=order[0],
            reason="按串行访问原则",
            arbiter="orchestrator",
            access_order=order,
        )
