def calculate_score(report):
    score = 100

    for r in report.results:
        if r.passed:
            continue
        if r.severity == "error":
            score -= 10
        elif r.severity == "warn":
            score -= 5
        elif r.severity == "info":
            score -= 1

    return max(0, min(100, score))
