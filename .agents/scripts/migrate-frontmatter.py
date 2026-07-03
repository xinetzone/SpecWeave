#!/usr/bin/env python3
"""批量迁移 TOML frontmatter 文件为 YAML+x-toml-ref 格式。

将项目中使用 +++ 包裹的 TOML frontmatter 迁移为 --- 包裹的 YAML frontmatter，
其余字段外置到 .meta/toml/ 目录下的外部 TOML 文件，通过 x-toml-ref 引用。

用法示例:
  python .agents/scripts/migrate-frontmatter.py --dry-run          # 预览变更
  python .agents/scripts/migrate-frontmatter.py --backup            # 备份后转换
  python .agents/scripts/migrate-frontmatter.py --verify            # 验证一致性
  python .agents/scripts/migrate-frontmatter.py --rollback          # 从备份恢复
  python .agents/scripts/migrate-frontmatter.py --path docs/        # 仅转换指定目录
  python .agents/scripts/migrate-frontmatter.py --report report.json  # 输出JSON报告
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.migrate_frontmatter import (
    _write_report,
    batch_convert,
    build_arg_parser,
    compute_toml_ref_path,
    convert_file,
    escape_yaml_string,
    extract_all_fields,
    generate_yaml_frontmatter,
    main,
    parse_frontmatter_unified,
    rollback,
    scan_files,
    setup_logging,
    verify_consistency,
)

if __name__ == "__main__":
    sys.exit(main())
