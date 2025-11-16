import pandas as pd
from .parse_mitre import heuristic_difficulty_score, heuristic_popularity_score


def compute_coverage(techniques, sigma_map):
    if not techniques:
        return 0.0, []
    covered = [t for t in techniques if t["id"].upper() in sigma_map]
    coverage_ratio = len(covered) / len(techniques)
    return coverage_ratio, covered


def compute_rule_density(techniques, sigma_map):
    rows = []
    for t in techniques:
        tid = t["id"].upper()
        rows.append(
            {
                "technique": tid,
                "name": t.get("name", ""),
                "rule_count": len(sigma_map.get(tid, [])),
            }
        )
    df = pd.DataFrame(rows, columns=["technique", "name", "rule_count"])
    return df


def compute_logsource_telemetry_metrics(techniques, sigma_map, rule_meta):
    rows = []
    for t in techniques:
        tid = t["id"].upper()
        rule_paths = sigma_map.get(tid, [])
        logsources = set()
        telemetry = set()
        for p in rule_paths:
            meta = rule_meta.get(p, {})
            logsources.add(
                (
                    meta.get("log_product"),
                    meta.get("log_service"),
                    meta.get("log_category"),
                )
            )
            for cat in meta.get("telemetry", []):
                telemetry.add(cat)
        logsources = {ls for ls in logsources if any(ls)}
        rows.append(
            {
                "technique": tid,
                "name": t.get("name", ""),
                "logsource_diversity": len(logsources),
                "telemetry_diversity": len(telemetry),
            }
        )
    df = pd.DataFrame(
        rows, columns=["technique", "name", "logsource_diversity", "telemetry_diversity"]
    )
    return df


def compute_weighted_metrics(techniques, sigma_map):
    rows = []
    for t in techniques:
        tid = t["id"].upper()
        rule_count = len(sigma_map.get(tid, []))
        diff = heuristic_difficulty_score(t.get("detection_text", ""))
        pop = heuristic_popularity_score(t)
        weighted = rule_count * pop / diff if diff > 0 else 0.0
        rows.append(
            {
                "technique": tid,
                "name": t.get("name", ""),
                "rule_count": rule_count,
                "difficulty_score": diff,
                "popularity_score": pop,
                "weighted_rule_score": weighted,
            }
        )
    df = pd.DataFrame(
        rows,
        columns=[
            "technique",
            "name",
            "rule_count",
            "difficulty_score",
            "popularity_score",
            "weighted_rule_score",
        ],
    )
    return df


def compute_technique_coupling(sigma_map, min_shared=2):
    techniques = list(sigma_map.keys())
    rows = []
    for i, t in enumerate(techniques):
        rules_t = set(sigma_map[t])
        coupling = 0
        for j, u in enumerate(techniques):
            if i == j:
                continue
            shared = rules_t.intersection(sigma_map[u])
            if len(shared) >= min_shared:
                coupling += 1
        rows.append({"technique": t, "coupling_score": coupling})
    return pd.DataFrame(rows, columns=["technique", "coupling_score"])
