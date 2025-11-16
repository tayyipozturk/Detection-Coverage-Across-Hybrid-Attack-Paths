import os

from scripts.download_mitre import download_mitre
from scripts.download_sigma import download_sigma
from scripts.parse_mitre import (
    load_mitre,
    get_cloud_techniques,
    get_lateral_techniques,
)
from scripts.parse_sigma import extract_sigma_mappings
from scripts.metrics import (
    compute_coverage,
    compute_rule_density,
    compute_logsource_telemetry_metrics,
    compute_weighted_metrics,
    compute_technique_coupling,
)
from scripts.visualize_basic import plot_coverage, plot_rule_density
from scripts.visualize_advanced import (
    scatter_difficulty_vs_rules,
    scatter_weighted_vs_rules,
    boxplot_logsource_telemetry,
    histogram_coupling,
)
from scripts.semantic_clustering import run_clustering
from scripts.attack_path import compute_path_coverage
from scripts.telemetry_gap import compute_telemetry_gap


def main():
    os.makedirs("output/figures", exist_ok=True)

    print("=== STEP 1: Download datasets ===")
    download_mitre()
    download_sigma()

    print("\n=== STEP 2: Parse MITRE ATT&CK ===")
    all_tech = load_mitre()
    cloud = get_cloud_techniques(all_tech)
    lateral = get_lateral_techniques(all_tech)
    print(f"[+] Total techniques: {len(all_tech)}")
    print(f"[+] Cloud techniques (heuristic): {len(cloud)}")
    print(f"[+] Lateral-movement techniques: {len(lateral)}")

    print("\n=== STEP 3: Parse Sigma rules ===")
    sigma_map, rule_meta = extract_sigma_mappings()

    print("\n=== STEP 4: Basic metrics ===")
    cloud_cov, _ = compute_coverage(cloud, sigma_map)
    lat_cov, _ = compute_coverage(lateral, sigma_map)
    print(f"[+] Cloud coverage (any rule):   {cloud_cov:.3f}")
    print(f"[+] Lateral coverage (any rule): {lat_cov:.3f}")

    df_cloud_density = compute_rule_density(cloud, sigma_map)
    df_lat_density = compute_rule_density(lateral, sigma_map)
    df_cloud_density.to_csv("output/rule_density_cloud.csv", index=False)
    df_lat_density.to_csv("output/rule_density_lateral.csv", index=False)
    print("[+] Saved basic density CSVs under output/")

    print("\n=== STEP 5: Advanced per-technique metrics ===")
    df_cloud_weight = compute_weighted_metrics(cloud, sigma_map)
    df_lat_weight = compute_weighted_metrics(lateral, sigma_map)
    df_cloud_logtele = compute_logsource_telemetry_metrics(cloud, sigma_map, rule_meta)
    df_lat_logtele = compute_logsource_telemetry_metrics(lateral, sigma_map, rule_meta)

    df_cloud_full = df_cloud_weight.merge(
        df_cloud_logtele, on=["technique", "name"], how="left"
    )
    df_lat_full = df_lat_weight.merge(
        df_lat_logtele, on=["technique", "name"], how="left"
    )
    df_cloud_full.to_csv("output/technique_metrics_cloud.csv", index=False)
    df_lat_full.to_csv("output/technique_metrics_lateral.csv", index=False)
    print("[+] Saved advanced technique metrics under output/")

    print("\n=== STEP 6: Technique coupling ===")
    df_coupling = compute_technique_coupling(sigma_map, min_shared=2)
    df_coupling.to_csv("output/technique_coupling.csv", index=False)
    print("[+] Saved technique_coupling.csv")

    print("\n=== STEP 7: Visualizations (basic) ===")
    if len(df_cloud_density) and len(df_lat_density):
        plot_coverage(cloud_cov, lat_cov)
        plot_rule_density(df_cloud_density, df_lat_density)
    else:
        print("[!] Skipping basic plots: density data empty.")

    print("\n=== STEP 8: Visualizations (advanced) ===")
    if len(df_cloud_full) and len(df_lat_full):
        scatter_difficulty_vs_rules(
            df_cloud_full,
            "Cloud Techniques: Difficulty vs Rule Count",
            "cloud_difficulty_vs_rules.png",
        )
        scatter_difficulty_vs_rules(
            df_lat_full,
            "Lateral Techniques: Difficulty vs Rule Count",
            "lateral_difficulty_vs_rules.png",
        )
        scatter_weighted_vs_rules(
            df_cloud_full,
            "Cloud Techniques: Weighted Rule Score vs Rule Count",
            "cloud_weighted_vs_rules.png",
        )
        scatter_weighted_vs_rules(
            df_lat_full,
            "Lateral Techniques: Weighted Rule Score vs Rule Count",
            "lateral_weighted_vs_rules.png",
        )
        boxplot_logsource_telemetry(df_cloud_full, df_lat_full)
    else:
        print("[!] Skipping advanced scatter/box plots: technique metrics empty.")

    histogram_coupling(
        df_coupling,
        "Technique Coupling Distribution (All Techniques)",
        "technique_coupling_hist.png",
    )

    print("\n=== STEP 9: Optional semantic clustering ===")
    run_clustering(rule_meta)

    print("\n=== STEP 10: Attack Path Coverage (Kill-chain DAG) ===")
    df_cloud_paths = compute_path_coverage(cloud, sigma_map)
    df_lat_paths = compute_path_coverage(lateral, sigma_map)

    df_cloud_paths.to_csv("output/attack_paths_cloud.csv", index=False)
    df_lat_paths.to_csv("output/attack_paths_lateral.csv", index=False)
    print("[+] Saved attack-path coverage CSVs")

    print("\n=== STEP 11: Telemetry Gap Analysis (MITRE vs Sigma) ===")
    df_cloud_tgap = compute_telemetry_gap(cloud, sigma_map, rule_meta)
    df_lat_tgap = compute_telemetry_gap(lateral, sigma_map, rule_meta)

    df_cloud_tgap.to_csv("output/telemetry_gap_cloud.csv", index=False)
    df_lat_tgap.to_csv("output/telemetry_gap_lateral.csv", index=False)
    print("[+] Saved telemetry gap CSVs")

    print("\n=== DONE ===")
    print("Check the 'output' directory for CSVs and 'output/figures' for figures.")


if __name__ == "__main__":
    main()
