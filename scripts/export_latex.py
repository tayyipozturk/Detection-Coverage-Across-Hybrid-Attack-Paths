import pandas as pd


def load_density():
    df_cloud = pd.read_csv("output/rule_density_cloud.csv")
    df_lat = pd.read_csv("output/rule_density_lateral.csv")
    return df_cloud, df_lat


def basic_stats(df_cloud, df_lat):
    stats = {
        "cloud_total": len(df_cloud),
        "lat_total": len(df_lat),
        "cloud_cov": (df_cloud["rule_count"] > 0).mean() if len(df_cloud) else 0,
        "lat_cov": (df_lat["rule_count"] > 0).mean() if len(df_lat) else 0,
        "cloud_mean": df_cloud["rule_count"].mean() if len(df_cloud) else 0,
        "lat_mean": df_lat["rule_count"].mean() if len(df_lat) else 0,
        "cloud_median": df_cloud["rule_count"].median() if len(df_cloud) else 0,
        "lat_median": df_lat["rule_count"].median() if len(df_lat) else 0,
    }
    return stats


def latex_summary_table(stats):
    return f"""\\begin{{table}}[!ht]
\\centering
\\begin{{tabular}}{{lcc}}
\\toprule
 & Cloud Techniques & Lateral Movement Techniques \\
\\midrule
# Techniques & {stats["cloud_total"]} & {stats["lat_total"]} \\
Coverage (rule>0) & {stats["cloud_cov"]:.2f} & {stats["lat_cov"]:.2f} \\
Mean Rule Density & {stats["cloud_mean"]:.2f} & {stats["lat_mean"]:.2f} \\
Median Rule Density & {stats["cloud_median"]:.0f} & {stats["lat_median"]:.0f} \\
\\bottomrule
\\end{{tabular}}
\\caption{{Summary of Sigma rule coverage and density for cloud vs lateral-movement techniques.}}
\\label{{tab:coverage-summary}}
\\end{{table}}"""


if __name__ == "__main__":
    df_c, df_l = load_density()
    s = basic_stats(df_c, df_l)
    print("\n=== LaTeX summary table ===\n")
    print(latex_summary_table(s))
    print("\n===========================\n")
