import os
import subprocess

SIGMA_DIR = os.path.join("data", "sigma")


def download_sigma():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(SIGMA_DIR):
        print("[+] Cloning SigmaHQ repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/SigmaHQ/sigma.git", SIGMA_DIR],
            check=True,
        )
    else:
        print("[+] SigmaHQ repo already exists, pulling latest changes...")
        subprocess.run(
            ["git", "-C", SIGMA_DIR, "pull"],
            check=True,
        )
    print(f"[+] Sigma rules available under {SIGMA_DIR}")


if __name__ == "__main__":
    download_sigma()
