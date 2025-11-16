# scripts/telemetry_gap.py
import pandas as pd


def compute_telemetry_gap(techniques, sigma_map, rule_meta):
    """
    techniques: list of techniques from load_mitre() (id, name, data_sources, vs.)
    sigma_map : {tech_id -> [rule_path, ...]}
    rule_meta : {rule_path -> {log_product, log_service, log_category, telemetry, ...}}

    Return:
        DataFrame: technique, required_telemetry, sigma_telemetry,
                   telemetry_coverage, telemetry_gap,
                   required_count, provided_count, gap_count
    """

    rows = []

    for t in techniques:
        tid = t["id"].upper()
        mitre_reqs = set([ds.strip() for ds in t.get("data_sources", []) if ds])

        if not mitre_reqs:
            continue

        sigma_tels = set()
        rule_paths = sigma_map.get(tid, [])

        for path in rule_paths:
            meta = rule_meta.get(path, {}) or {}
            lp = meta.get("log_product")
            ls = meta.get("log_service")
            lc = meta.get("log_category")

            for x in (lp, ls, lc):
                if x:
                    sigma_tels.add(str(x).strip())

            for cat in meta.get("telemetry", []):
                sigma_tels.add(str(cat).strip())

        overlap = mitre_reqs & sigma_tels

        if len(mitre_reqs) > 0:
            coverage = len(overlap) / len(mitre_reqs)
        else:
            coverage = 0.0

        rows.append(
            {
                "technique": tid,
                "name": t.get("name", ""),
                "required_telemetry": "; ".join(sorted(mitre_reqs)),
                "sigma_telemetry": "; ".join(sorted(sigma_tels)),
                "telemetry_coverage": coverage,
                "telemetry_gap": 1.0 - coverage,
                "required_count": len(mitre_reqs),
                "provided_count": len(sigma_tels),
                "gap_count": len(mitre_reqs - sigma_tels),
            }
        )

    df = pd.DataFrame(
        rows,
        columns=[
            "technique",
            "name",
            "required_telemetry",
            "sigma_telemetry",
            "telemetry_coverage",
            "telemetry_gap",
            "required_count",
            "provided_count",
            "gap_count",
        ],
    )

    return df
