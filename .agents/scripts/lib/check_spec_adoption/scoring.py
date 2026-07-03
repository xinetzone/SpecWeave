from datetime import datetime
from pathlib import Path

from .constants import FM_PATTERN, PROFILES
from .check_frontmatter import check_frontmatter, init_fm_issues
from .check_links import check_links
from .check_structure import check_file_size, check_nav_and_atomization, check_pattern_references


def get_grade(score):
    if score >= 90:
        return 'A (优秀)'
    elif score >= 80:
        return 'B (良好)'
    elif score >= 70:
        return 'C (需改进)'
    elif score >= 60:
        return 'D (较差)'
    else:
        return 'F (不及格)'


def compute_metrics(md_files, project_root, since_date=None):
    metrics = {
        'total_files': 0,
        'files_with_fm': 0,
        'fm_compliant': 0,
        'fm_issues': init_fm_issues(),
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

    since_dt = None
    if since_date:
        try:
            since_dt = datetime.strptime(since_date, '%Y-%m-%d')
        except ValueError:
            pass

    for fpath in md_files:
        rel_path = None
        try:
            rel_path = fpath.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = str(fpath)

        if since_dt:
            try:
                mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
                if mtime < since_dt:
                    continue
            except OSError:
                pass

        metrics['total_files'] += 1

        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception:
            continue

        fm_match = FM_PATTERN.match(content)
        if fm_match:
            metrics['files_with_fm'] += 1
            fm_text = fm_match.group(1)
            fm_issues, is_compliant, has_source = check_frontmatter(fm_text)

            for issue_key, count in fm_issues.items():
                metrics['fm_issues'][issue_key] += count

            if is_compliant:
                metrics['fm_compliant'] += 1

            if has_source:
                metrics['source_traceable'] += 1
        else:
            metrics['fm_issues']['missing_id'] += 1
            metrics['fm_issues']['missing_xref'] += 1

        links_total, links_valid, links_broken = check_links(content, fpath)
        metrics['links_total'] += links_total
        metrics['links_valid'] += links_valid
        metrics['links_broken'] += links_broken

        if check_file_size(content):
            metrics['large_files'] += 1

        has_nav_links, is_atomized = check_nav_and_atomization(content, rel_path)
        if has_nav_links:
            metrics['nav_links_present'] += 1
        if is_atomized:
            metrics['atomized_files'] += 1

        pattern_count, has_pattern_refs = check_pattern_references(content)
        if has_pattern_refs:
            metrics['pattern_references'] += pattern_count
            metrics['files_with_pattern_refs'] += 1

        metrics['files_scanned'].append(rel_path)

    return metrics


def compute_scores(metrics, weights=None):
    scores = {}
    total = metrics['total_files']
    if total == 0:
        return {'error': 'no_files'}

    with_fm = metrics['files_with_fm']
    scores['frontmatter_coverage'] = round(with_fm / total * 100, 1) if total > 0 else 0
    scores['frontmatter_compliance'] = round(metrics['fm_compliant'] / max(with_fm, 1) * 100, 1)
    scores['link_validity'] = round(metrics['links_valid'] / max(metrics['links_total'], 1) * 100, 1)
    scores['source_traceability'] = round(metrics['source_traceable'] / max(with_fm, 1) * 100, 1)
    scores['pattern_reference_rate'] = round(metrics['files_with_pattern_refs'] / max(total, 1) * 100, 1)
    scores['large_file_ratio'] = round(metrics['large_files'] / max(total, 1) * 100, 1)
    scores['nav_link_compliance'] = round(metrics['nav_links_present'] / max(metrics['atomized_files'] + 1, 1) * 100, 1)

    if weights is None:
        weights = PROFILES['docs']['weights']

    overall = 0.0
    weight_sum = 0.0
    for metric_key, w in weights.items():
        if metric_key == 'large_file_ratio_inverted':
            score_val = max(0, 100 - scores['large_file_ratio'])
            overall += score_val * w
            weight_sum += w
        elif metric_key in scores:
            overall += scores[metric_key] * w
            weight_sum += w

    if weight_sum > 0:
        overall = overall / weight_sum * sum(weights.values())
    scores['overall_adoption_score'] = round(overall, 1)
    scores['weights_used'] = weights

    return scores
