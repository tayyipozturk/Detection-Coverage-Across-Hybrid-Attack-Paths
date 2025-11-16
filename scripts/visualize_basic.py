import os
import matplotlib.pyplot as plt


def plot_coverage(cloud_cov, lat_cov, out_dir="output/figures"):
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.bar(["Cloud", "Lateral"], [cloud_cov, lat_cov])
    plt.ylim(0, 1)
    plt.ylabel("Coverage Ratio")
    plt.title("Cloud vs Lateral Movement Coverage")
    plt.tight_layout()
    out_path = os.path.join(out_dir, "cloud_vs_lateral_coverage.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")


def plot_rule_density(df_cloud, df_lat, out_dir="output/figures"):
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(7, 5))
    plt.boxplot(
        [df_cloud["rule_count"], df_lat["rule_count"]],
        labels=["Cloud", "Lateral"],
    )
    plt.ylabel("Rule Count")
    plt.title("Rule Density Comparison")
    plt.tight_layout()
    out_path = os.path.join(out_dir, "rule_density_boxplot.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[+] Saved {out_path}")
