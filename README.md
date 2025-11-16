# Advanced Detection Rule Coverage Analysis

This repository implements a complete, research-grade analysis pipeline for:

- **MITRE ATT&CK Enterprise** adversary techniques  
- **SigmaHQ public detection rules**

The goal is to quantify and compare **detection engineering maturity** across:

- **Cloud-compromise techniques**
- **Lateral-movement techniques**

The pipeline produces both basic and advanced metrics, visualizations, and structural insights into the defensive coverage of hybrid attack paths.

---

## 🔍 Features and Metrics

### **1. Basic Detection Coverage**
- Binary coverage (any Sigma rule mapped to the technique)
- Rule density (number of rules per technique)
- Cloud vs. Lateral movement comparison

### **2. Advanced Per-Technique Metrics**
Includes:

| Metric | Description |
|--------|-------------|
| Difficulty score | Heuristic estimation of technique complexity |
| Popularity score | Derived from community rule prevalence |
| Weighted score | Combines rule density, popularity, and difficulty |
| Logsource diversity | Count of distinct Sigma logsources |
| Telemetry diversity | High-level telemetry types derived from logsources |

### **3. Technique Coupling**
- Shared-rule graph construction  
- Coupling score per technique  
- Histogram visualization of coupling distribution  

### **4. Kill-Chain Attack-Path Coverage**
- Cloud-phase path sequences  
- Lateral-movement path sequences  
- Coverage per path (≥1 relevant Sigma rule)  
- Produces `attack_paths_cloud.csv` and `attack_paths_lateral.csv`

### **5. Telemetry Gap Analysis (MITRE vs Sigma)**
- Compares MITRE `x_mitre_data_sources` with Sigma telemetry
- Identifies:
  - Required telemetry
  - Provided telemetry
  - Telemetry coverage ratio
  - Telemetry gap size
- Outputs:
  - `telemetry_gap_cloud.csv`
  - `telemetry_gap_lateral.csv`

> **Note:** If the ATT&CK JSON snapshot lacks data-source metadata, gap CSVs may be empty. The module still runs end-to-end.

### **6. Optional Semantic Clustering**
If `sentence-transformers` is installed:
- Embeds Sigma rules
- Clusters them using KMeans
- Produces `semantic_clusters.csv`

---

## 📦 Installation

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

pip install -r requirements.txt
