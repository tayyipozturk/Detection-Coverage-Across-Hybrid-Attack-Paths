import json
import os

MITRE_FILE = os.path.join("data", "enterprise-attack.json")


def load_mitre():
    with open(MITRE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    techniques = []
    for obj in data.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue

        tech_id = None
        for ref in obj.get("external_references", []):
            ext_id = ref.get("external_id", "")
            if ext_id.startswith("T"):
                tech_id = ext_id
                break

        if not tech_id:
            continue

        platforms = obj.get("x_mitre_platforms", [])
        killchain_phases = obj.get("kill_chain_phases", [])
        killchain = [p.get("phase_name") for p in killchain_phases if "phase_name" in p]

        detection_text = obj.get("x_mitre_detection", "") or ""
        description = obj.get("description", "") or ""

        techniques.append(
            {
                "id": tech_id,
                "name": obj.get("name", ""),
                "platforms": platforms,
                "killchain": killchain,
                "detection_text": detection_text,
                "description": description,
                "revoked": obj.get("revoked", False),
                "deprecated": obj.get("x_mitre_deprecated", False),
            }
        )

    return techniques


def get_cloud_techniques(techniques):
    # Broad heuristic for cloud-related platforms
    cloud_keys = {
        "AWS",
        "AZURE",
        "GCP",
        "AZURE AD",
        "OFFICE 365",
        "SAAS",
        "IAAS",
        "GOOGLE WORKSPACE",
        "GOOGLE CLOUD PLATFORM",
        "MICROSOFT 365",
        "O365",
        "CONTAINER",
        "KUBERNETES",
    }
    cloud = []
    for t in techniques:
        plats = [p.upper() for p in (t.get("platforms") or [])]
        if any(any(k in p for k in cloud_keys) for p in plats):
            cloud.append(t)
    return cloud


def get_lateral_techniques(techniques):
    return [t for t in techniques if "lateral-movement" in (t.get("killchain") or [])]


def heuristic_difficulty_score(detection_text: str) -> float:
    """Simple heuristic: longer, more complex detection guidance -> higher difficulty.
    Also look for words like 'hard', 'difficult', 'complex', 'correlate'.
    Score in [1, 3]."""
    if not detection_text:
        return 1.5
    txt = detection_text.lower()
    length_score = min(len(txt) / 400.0, 2.0)
    keyword_boost = 0.0
    for kw in ["complex", "difficult", "hard", "correlat", "behavior", "anomaly"]:
        if kw in txt:
            keyword_boost += 0.3
    score = 1.0 + length_score + keyword_boost
    if score < 1.0:
        score = 1.0
    if score > 3.0:
        score = 3.0
    return score


def heuristic_popularity_score(tech) -> float:
    """Heuristic popularity: non-deprecated, non-revoked techniques get higher scores.
    Score in [0.5, 1.5]."""
    base = 1.0
    if tech.get("revoked"):
        base -= 0.3
    if tech.get("deprecated"):
        base -= 0.2
    if base < 0.5:
        base = 0.5
    if base > 1.5:
        base = 1.5
    return base


if __name__ == "__main__":
    all_tech = load_mitre()
    cloud = get_cloud_techniques(all_tech)
    lat = get_lateral_techniques(all_tech)
    print("Total techniques:", len(all_tech))
    print("Cloud techniques:", len(cloud))
    print("Lateral-movement techniques:", len(lat))
