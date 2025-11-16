import pandas as pd

def build_killchain_graph(techniques):
    edges=[]
    for t in techniques:
        phases=t.get("killchain") or []
        for i in range(len(phases)-1):
            edges.append((phases[i], phases[i+1], t["id"]))
    return edges

def compute_path_coverage(techniques, sigma_map):
    rows=[]
    for t in techniques:
        covered = t["id"].upper() in sigma_map
        rows.append({
            "technique":t["id"],
            "phase_sequence":"->".join(t.get("killchain") or []),
            "covered":1 if covered else 0
        })
    return pd.DataFrame(rows)
