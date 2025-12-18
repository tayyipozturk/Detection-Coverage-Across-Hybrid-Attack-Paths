import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# --- CONFIGURATION ---
# Path to your Sigma "rules" directory (change this if yours is different)
SIGMA_RULES_DIR = "../data/sigma/rules" 

# Load your existing technique definitions
try:
    cloud_techniques = set(pd.read_csv('../output/rule_density_cloud.csv')['technique'])
    lateral_techniques = set(pd.read_csv('../output/rule_density_lateral.csv')['technique'])
except FileNotFoundError:
    print("Error: Could not find rule_density_cloud.csv or rule_density_lateral.csv.")
    exit()

data = []

print(f"Scanning rules in {SIGMA_RULES_DIR}...")

# Walk through the Sigma directory
for root, dirs, files in os.walk(SIGMA_RULES_DIR):
    for file in files:
        if file.endswith(".yml") or file.endswith(".yaml"):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Parse YAML safely
                    rule = yaml.safe_load(f)
                    
                    if not rule or 'date' not in rule or 'tags' not in rule:
                        continue

                    # Extract Date
                    date_str = str(rule['date'])
                    try:
                        # Handle varied date formats (YYYY/MM/DD)
                        rule_date = pd.to_datetime(date_str, errors='coerce')
                        if pd.isnull(rule_date): continue
                    except:
                        continue

                    # Check Tags for Match
                    rule_tags = rule['tags']
                    is_cloud = False
                    is_lateral = False
                    
                    # Normalize tags (e.g., attack.t1098 -> T1098)
                    for tag in rule_tags:
                        clean_tag = tag.lower().replace('attack.', '').upper()
                        if clean_tag in cloud_techniques:
                            is_cloud = True
                        if clean_tag in lateral_techniques:
                            is_lateral = True
                    
                    # Assign Category (Prioritize Dual use if needed, or count for both)
                    if is_cloud:
                        data.append({'Date': rule_date, 'Type': 'Cloud'})
                    if is_lateral:
                        # Note: A rule can be both! We count it for both timelines.
                        data.append({'Date': rule_date, 'Type': 'Lateral'})

            except Exception as e:
                # Skip unreadable files
                continue

# Create DataFrame
df = pd.DataFrame(data)

if df.empty:
    print("No matching rules found! Check your SIGMA_RULES_DIR path.")
    exit()

# Group by Year and Type
df['Year'] = df['Date'].dt.year
df = df[df['Year'] >= 2017] # Filter out ancient/bad dates
timeline = df.groupby(['Year', 'Type']).size().unstack(fill_value=0)

# Calculate Cumulative Sum (Growth over time)
timeline_cumulative = timeline.cumsum()

# --- PLOTTING ---
plt.figure(figsize=(10, 6))
plt.plot(timeline_cumulative.index, timeline_cumulative.get('Cloud', []), 
         marker='o', label='Cloud Rules', color='#1f77b4', linewidth=2.5)
plt.plot(timeline_cumulative.index, timeline_cumulative.get('Lateral', []), 
         marker='s', label='Lateral Movement Rules', color='#ff7f0e', linewidth=2.5)

plt.title('Evolution of Detection Coverage: Cloud vs. Lateral Movement')
plt.xlabel('Year')
plt.ylabel('Cumulative Number of Rules')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()

plt.savefig('../output/figures/timeline_growth.png')
print("Timeline chart saved as 'timeline_growth.png'")