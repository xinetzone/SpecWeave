from pathlib import Path

from lib.markdown import find_markdown_files


def collect_md_files(target_dir, exclude_dirs, exclude_files):
    md_files = find_markdown_files(target_dir, exclude_dirs=exclude_dirs)
    if exclude_dirs:
        dir_name_excludes = {d for d in exclude_dirs if '/' not in d}
        path_prefix_excludes = {d.rstrip('/') + '/' for d in exclude_dirs if '/' in d}
        md_files_filtered = []
        for f in md_files:
            rel_posix = f.relative_to(target_dir).as_posix()
            rel_parts = rel_posix.split('/')
            excluded = False
            for part in rel_parts[:-1]:
                if part in dir_name_excludes:
                    excluded = True
                    break
            if not excluded:
                for prefix in path_prefix_excludes:
                    if rel_posix.startswith(prefix):
                        excluded = True
                        break
            if not excluded:
                md_files_filtered.append(f)
        md_files = md_files_filtered
    if exclude_files:
        md_files = [f for f in md_files if f.name not in exclude_files]
    return md_files
