import os
import yaml

SIGMA_ROOT = os.path.join("data", "sigma")


def find_rules_dir():
    candidates = [
        "rules",
        os.path.join("rules", "cloud"),
        os.path.join("rules", "windows"),
        os.path.join("rules", "linux"),
        os.path.join("rules", "network"),
        os.path.join("rules", "other"),
    ]
    for c in candidates:
        path = os.path.join(SIGMA_ROOT, c)
        if os.path.isdir(path):
            return path
    raise RuntimeError("Sigma rule directory not found under data/sigma. Check repo structure.")


def categorize_telemetry(rule: dict) -> set:
    """Very rough heuristic based on 'logsource' and 'detection' fields."""
    categories = set()
    logsource = rule.get("logsource", {}) or {}
    product = (logsource.get("product") or "").lower()
    service = (logsource.get("service") or "").lower()
    category = (logsource.get("category") or "").lower()

    ls_combo = " ".join([product, service, category])

    if any(x in ls_combo for x in ["sysmon", "process_creation", "process"]):
        categories.add("process")
    if any(x in ls_combo for x in ["security", "authentication", "logon", "signin"]):
        categories.add("auth")
    if any(x in ls_combo for x in ["dns", "proxy", "netflow", "firewall", "network"]):
        categories.add("network")
    if "registry" in ls_combo:
        categories.add("registry")
    if "file" in ls_combo or "filesystem" in ls_combo:
        categories.add("file")
    if any(x in ls_combo for x in ["cloudtrail", "azure", "gcp", "cloud"]):
        categories.add("cloud_api")

    detection = rule.get("detection", {}) or {}
    det_text = str(detection).lower()
    if "commandline" in det_text or "image" in det_text:
        categories.add("process")
    if "registry" in det_text:
        categories.add("registry")
    if "dst_port" in det_text or "dst_ip" in det_text:
        categories.add("network")

    if not categories:
        categories.add("other")

    return categories


def extract_sigma_mappings():
    rules_dir = find_rules_dir()
    print(f"[+] Using Sigma rules from: {rules_dir}")
    technique_map = {}
    rule_meta = {}

    for root, _, files in os.walk(rules_dir):
        for file in files:
            if not file.endswith((".yml", ".yaml")):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    rule = yaml.safe_load(f) or {}
            except Exception:
                continue

            tags = rule.get("tags", [])
            if not isinstance(tags, list):
                continue

            techniques = []
            for t in tags:
                if isinstance(t, str) and t.lower().startswith("attack.t"):
                    tech = t.split("attack.", 1)[-1].upper()
                    techniques.append(tech)

            if not techniques:
                continue

            logsource = rule.get("logsource", {}) or {}
            product = logsource.get("product")
            service = logsource.get("service")
            category = logsource.get("category")
            telemetry = categorize_telemetry(rule)

            meta = {
                "title": rule.get("title", ""),
                "log_product": product,
                "log_service": service,
                "log_category": category,
                "telemetry": sorted(list(telemetry)),
                "path": path,
            }
            rule_meta[path] = meta

            for tech in techniques:
                technique_map.setdefault(tech, []).append(path)

    print(f"[+] Extracted mappings for {len(technique_map)} ATT&CK techniques from Sigma.")
    return technique_map, rule_meta


if __name__ == "__main__":
    m, meta = extract_sigma_mappings()
    print("Sample techniques:", list(m.keys())[:5])
