from typing import Dict, List, Optional, Type

from .checkers.base import BaseDiagramChecker
from .checkers.security import SecurityChecker
from .checkers import (
    FlowchartChecker,
    StateDiagramChecker,
    SequenceDiagramChecker,
    ClassDiagramChecker,
    ErDiagramChecker,
    MindmapChecker,
    PieChecker,
    GanttChecker,
    TimelineChecker,
    XyChartChecker,
    QuadrantChecker,
)
from .fixers import (
    FlowchartFixer,
    StateDiagramFixer,
    SequenceDiagramFixer,
    ClassDiagramFixer,
    ErDiagramFixer,
    MindmapFixer,
    PieFixer,
    GanttFixer,
    GenericFixer,
)


class CheckerRegistry:
    def __init__(self):
        self._checkers: Dict[str, Type[BaseDiagramChecker]] = {}
        self._security_checker: Optional[SecurityChecker] = None

    def register(self, checker_class: Type[BaseDiagramChecker]) -> None:
        instance = checker_class()
        dia_type = instance.get_diagram_type()
        self._checkers[dia_type] = checker_class

    def get_checker(self, diagram_type: str) -> Optional[BaseDiagramChecker]:
        cls = self._checkers.get(diagram_type)
        if cls:
            return cls()
        return None

    def set_security_checker(self, checker: SecurityChecker) -> None:
        self._security_checker = checker

    def get_security_checker(self) -> Optional[SecurityChecker]:
        return self._security_checker

    def get_all_types(self) -> List[str]:
        return list(self._checkers.keys())


class FixerRegistry:
    def __init__(self):
        self._fixers: Dict[str, object] = {}

    def register(self, diagram_type: str, fixer) -> None:
        self._fixers[diagram_type] = fixer

    def get_fixer(self, diagram_type: str):
        return self._fixers.get(diagram_type)

    def get_all_types(self) -> List[str]:
        return list(self._fixers.keys())


def create_default_checker_registry() -> CheckerRegistry:
    registry = CheckerRegistry()
    registry.register(FlowchartChecker)
    registry.register(StateDiagramChecker)
    registry.register(SequenceDiagramChecker)
    registry.register(ClassDiagramChecker)
    registry.register(ErDiagramChecker)
    registry.register(MindmapChecker)
    registry.register(PieChecker)
    registry.register(GanttChecker)
    registry.register(TimelineChecker)
    registry.register(XyChartChecker)
    registry.register(QuadrantChecker)
    registry.set_security_checker(SecurityChecker())
    return registry


def create_default_fixer_registry() -> FixerRegistry:
    registry = FixerRegistry()
    registry.register("flowchart", FlowchartFixer())
    registry.register("stateDiagram", StateDiagramFixer())
    registry.register("sequenceDiagram", SequenceDiagramFixer())
    registry.register("classDiagram", ClassDiagramFixer())
    registry.register("erDiagram", ErDiagramFixer())
    registry.register("mindmap", MindmapFixer())
    registry.register("pie", PieFixer())
    registry.register("gantt", GanttFixer())
    registry.register("timeline", GenericFixer("timeline"))
    registry.register("xychart-beta", GenericFixer("xychart-beta"))
    registry.register("quadrantchart", GenericFixer("quadrantchart"))
    return registry
