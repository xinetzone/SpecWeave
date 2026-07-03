from dataclasses import dataclass, field


@dataclass
class Issue:
    severity: str
    category: str
    file: str
    message: str
    fixable: bool = False


@dataclass
class AuditResult:
    total_md_files: int = 0
    md_with_frontmatter: int = 0
    md_with_x_toml_ref: int = 0
    total_toml_files: int = 0
    toml_with_valid_id: int = 0
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)
    by_category: dict = field(default_factory=dict)
    by_directory: dict = field(default_factory=dict)

    def add_error(self, category: str, file_path: str, message: str, fixable: bool = False):
        self.errors.append(Issue('error', category, file_path, message, fixable))

    def add_warning(self, category: str, file_path: str, message: str, fixable: bool = False):
        self.warnings.append(Issue('warning', category, file_path, message, fixable))
