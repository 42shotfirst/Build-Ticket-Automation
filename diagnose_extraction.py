#!/usr/bin/env python3
import json
import sys

# Read the comprehensive extract JSON
with open('Microsoft Active Directory DR_comprehensive_extract.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("DIAGNOSTIC: What's in the production file")
print("=" * 80)

# Check Build_ENV
build_env = data['sheets']['Build_ENV']['raw_data']
print("\nBuild_ENV (first 15 rows):")
for i, row in enumerate(build_env[:15]):
    if isinstance(row, dict) and any(row.values()):
        print(f"Row {i}: {row.get('0', '')[:30]:30s} = {row.get('2', '')}")

# Check Resources for VM section
resources = data['sheets']['Resources']['raw_data']
print("\n\nResources sheet - VM section (rows 90-120):")
for i in range(90, min(120, len(resources))):
    row = resources[i]
    if isinstance(row, dict):
        col0 = str(row.get('0', '')).strip()
        col2 = str(row.get('2', '')).strip()
        if col0 or col2:
            print(f"Row {i:3d}: {col0:35s} = {col2}")

# Check NSG
nsg = data['sheets']['NSG']['raw_data']
print("\n\nNSG sheet (first 15 rows):")
for i, row in enumerate(nsg[:15]):
    if isinstance(row, dict) and any(row.values()):
        values = [str(row.get(str(j), ''))[:15] for j in range(5)]
        print(f"Row {i}: " + " | ".join(values))
