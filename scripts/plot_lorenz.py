import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
CLOUD_FILE = '../output/rule_density_cloud.csv'
LATERAL_FILE = '../output/rule_density_lateral.csv'
OUTPUT_IMAGE = '../output/figures/lorenz_curve.png'

def calculate_gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    array = array.flatten()
    if np.amin(array) < 0:
        array -= np.amin(array) # Values cannot be negative
    array = array + 0.0000001 # Values cannot be 0
    array = np.sort(array) # Values must be sorted
    index = np.arange(1, array.shape[0]+1)
    n = array.shape[0]
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array)))

def plot_lorenz_curve(data, label, ax, color):
    """Plot Lorenz Curve for a specific dataset."""
    X = data['rule_count'].values
    X = np.sort(X)
    
    # Cumulative sum of rules
    Y = np.cumsum(X) / np.sum(X)
    
    # Cumulative % of population (Techniques)
    X_lorenz = np.arange(1, len(X) + 1) / len(X)
    
    # Add 0,0 point for the plot to start at origin
    X_lorenz = np.insert(X_lorenz, 0, 0)
    Y = np.insert(Y, 0, 0)
    
    gini = calculate_gini(X)
    ax.plot(X_lorenz, Y, label=f'{label} (Gini: {gini:.2f})', linewidth=2.5, color=color)

# --- MAIN EXECUTION ---
try:
    df_cloud = pd.read_csv(CLOUD_FILE)
    df_lateral = pd.read_csv(LATERAL_FILE)
except FileNotFoundError:
    print("Error: CSV files not found. Make sure rule_density_cloud.csv and rule_density_lateral.csv are in the folder.")
    exit()

fig, ax = plt.subplots(figsize=(8, 8))

# Plot Cloud (Blue)
plot_lorenz_curve(df_cloud, 'Cloud', ax, '#1f77b4')

# Plot Lateral (Orange)
plot_lorenz_curve(df_lateral, 'Lateral Movement', ax, '#ff7f0e')

# Plot "Perfect Equality" Line (Diagonal)
ax.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Perfect Equality', alpha=0.7)

# Formatting
ax.set_title('Lorenz Curve: Inequality of Detection Rule Distribution', fontsize=14)
ax.set_xlabel('Cumulative % of Techniques (Sorted by Density)', fontsize=12)
ax.set_ylabel('Cumulative % of Detection Rules', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE)
print(f"Lorenz curve saved as '{OUTPUT_IMAGE}'")
plt.show()