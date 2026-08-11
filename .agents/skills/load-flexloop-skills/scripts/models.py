from dataclasses import dataclass, field, asdict
from enum import Enum


class SkillStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class SkillMetadata:
    name: str
    skill_path: str
    source: str
    description: str = ""
    version: str = ""
    status: SkillStatus = SkillStatus.OK
    issues: list[str] = field(default_factory=list)
    raw_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class ScanError:
    file_path: str
    error_type: str
    message: str
    suggestion: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScanResult:
    scan_time: str = ""
    scan_dirs: list[str] = field(default_factory=list)
    skills: list[SkillMetadata] = field(default_factory=list)
    errors: list[ScanError] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scan_time": self.scan_time,
            "scan_dirs": self.scan_dirs,
            "skills": [s.to_dict() for s in self.skills],
            "errors": [e.to_dict() for e in self.errors],
            "conflicts": self.conflicts,
        }

    def add_stats(self) -> dict:
        total = len(self.skills)
        ok_count = sum(1 for s in self.skills if s.status == SkillStatus.OK)
        warning_count = sum(1 for s in self.skills if s.status == SkillStatus.WARNING)
        error_count = sum(1 for s in self.skills if s.status == SkillStatus.ERROR)
        return {
            "total": total,
            "ok": ok_count,
            "warning": warning_count,
            "error": error_count,
            "conflicts": len(self.conflicts),
        }
