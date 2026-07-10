from dataclasses import dataclass, field
from typing import Any


def default_metrics() -> dict[str, Any]:
    return {
        'total_files': 0,
        'files_with_fm': 0,
        'fm_compliant': 0,
        'fm_issues': {
            'missing_id': 0,
            'missing_xref': 0,
            'has_forbidden_fields': 0,
            'has_nested': 0,
            'bloated_fm': 0,
        },
        'links_total': 0,
        'links_valid': 0,
        'links_broken': 0,
        'large_files': 0,
        'atomized_files': 0,
        'pattern_references': 0,
        'files_with_pattern_refs': 0,
        'nav_links_present': 0,
        'source_traceable': 0,
        'files_scanned': [],
    }


@dataclass
class MetricsResult:
    total_files: int = 0
    files_with_fm: int = 0
    fm_compliant: int = 0
    fm_issues: dict[str, int] = field(default_factory=lambda: {
        'missing_id': 0,
        'missing_xref': 0,
        'has_forbidden_fields': 0,
        'has_nested': 0,
        'bloated_fm': 0,
    })
    links_total: int = 0
    links_valid: int = 0
    links_broken: int = 0
    large_files: int = 0
    atomized_files: int = 0
    pattern_references: int = 0
    files_with_pattern_refs: int = 0
    nav_links_present: int = 0
    source_traceable: int = 0
    files_scanned: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'total_files': self.total_files,
            'files_with_fm': self.files_with_fm,
            'fm_compliant': self.fm_compliant,
            'fm_issues': self.fm_issues.copy(),
            'links_total': self.links_total,
            'links_valid': self.links_valid,
            'links_broken': self.links_broken,
            'large_files': self.large_files,
            'atomized_files': self.atomized_files,
            'pattern_references': self.pattern_references,
            'files_with_pattern_refs': self.files_with_pattern_refs,
            'nav_links_present': self.nav_links_present,
            'source_traceable': self.source_traceable,
            'files_scanned': self.files_scanned.copy(),
        }
