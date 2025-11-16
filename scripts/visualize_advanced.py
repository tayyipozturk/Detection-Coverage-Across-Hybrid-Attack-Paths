import os
import matplotlib.pyplot as plt


def _ensure_dir(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def scatter_difficulty_vs_rules(df, title, filename, out_dir="output/figures"):
    _ensure_dir(out_dir)
    plt.figure(figsize=(7, 5))
    plt.scatter(df["difficulty_score"], df["rule_count"])
    plt.xlabel("Heuristic Difficulty Score")
    plt.ylabel("Rule Count")
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(out_dir, filename)
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")


def scatter_weighted_vs_rules(df, title, filename, out_dir="output/figures"):
    _ensure_dir(out_dir)
    plt.figure(figsize=(7, 5))
    plt.scatter(df["rule_count"], df["weighted_rule_score"])
    plt.xlabel("Rule Count")
    plt.ylabel("Weighted Rule Score")
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(out_dir, filename)
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")


def boxplot_logsource_telemetry(df_cloud, df_lat, out_dir="output/figures"):
    _ensure_dir(out_dir)
    plt.figure(figsize=(7, 5))
    plt.boxplot(
        [df_cloud["logsource_diversity"], df_lat["logsource_diversity"]],
        labels=["Cloud", "Lateral"],
    )
    plt.ylabel("# Distinct Logsources")
    plt.title("Logsource Diversity")
    plt.tight_layout()
    out_path = os.path.join(out_dir, "logsource_diversity_boxplot.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")

    plt.figure(figsize=(7, 5))
    plt.boxplot(
        [df_cloud["telemetry_diversity"], df_lat["telemetry_diversity"]],
        labels=["Cloud", "Lateral"],
    )
    plt.ylabel("# Telemetry Categories")
    plt.title("Telemetry Diversity")
    plt.tight_layout()
    out_path = os.path.join(out_dir, "telemetry_diversity_boxplot.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")


def histogram_coupling(df_couple, title, filename, out_dir="output/figures"):
    _ensure_dir(out_dir)
    plt.figure(figsize=(7, 5))
    plt.hist(df_couple["coupling_score"], bins=20)
    plt.xlabel("Coupling Score (# of related techniques)")
    plt.ylabel("Count of techniques")
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(out_dir, filename)
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")
