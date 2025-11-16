import os

import pandas as pd

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans
    HAVE_EMBED = True
except Exception:
    HAVE_EMBED = False


def build_rule_corpus(rule_meta, max_rules=1000):
    items = list(rule_meta.items())
    if len(items) > max_rules:
        items = items[:max_rules]
    texts = []
    paths = []
    for path, meta in items:
        title = meta.get("title") or ""
        logs = " ".join(
            filter(
                None,
                [
                    meta.get("log_product"),
                    meta.get("log_service"),
                    meta.get("log_category"),
                ],
            )
        )
        telemetry = " ".join(meta.get("telemetry", []))
        text = f"{title}. Logs: {logs}. Telemetry: {telemetry}"
        texts.append(text)
        paths.append(path)
    return paths, texts


def run_clustering(rule_meta, out_csv="output/semantic_clusters.csv", n_clusters=10):
    if not HAVE_EMBED:
        print("[!] sentence-transformers / scikit-learn not available, skipping semantic clustering.")
        return

    os.makedirs("output", exist_ok=True)
    paths, texts = build_rule_corpus(rule_meta)
    if not texts:
        print("[!] No rules to cluster.")
        return

    print(f"[+] Encoding {len(texts)} rules with sentence-transformers...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode(texts, show_progress_bar=True)

    print(f"[+] Running KMeans(n_clusters={n_clusters})...")
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(emb)

    rows = []
    for path, label in zip(paths, labels):
        meta = rule_meta.get(path, {})
        rows.append(
            {
                "path": path,
                "cluster": int(label),
                "title": meta.get("title", ""),
                "log_product": meta.get("log_product", ""),
                "log_service": meta.get("log_service", ""),
                "log_category": meta.get("log_category", ""),
                "telemetry": " ".join(meta.get("telemetry", [])),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"[+] Saved semantic clusters to {out_csv}")


if __name__ == "__main__":
    print("This module is intended to be called from main.py where rule_meta is available.")
