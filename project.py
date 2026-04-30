import pandas as pd
import streamlit
import pandas
import networkx
import plotly
import requests



df = pd.read_csv('nwsl_stadium.csv')

# # ============================================
# # CHECK 1: Column Names
# # ============================================
print("=== COLUMN NAMES ===")
for col in df.columns:
    print(f"  '{col}'")

# # ============================================
# # CHECK 2: Status Column Values
# # # ============================================
# STATUS_COLUMNS = [
#     'accessible_seating',
#     'accessible_seating_standard_ticket_exchange',
#     'assisted_listening_devices',
#     'videoboard_closed_captioning',
#     'public_elevators',
#     'wheelchair_services',
#     'service_animals',
#     'sensory_accommodations',
#     'gender_neutral_restrooms',
#     'parking_accessibility',
#     'nursing_rooms',
#     'interpretation_services',
# ]

# print("\n=== STATUS COLUMN VALUES ===")
# all_clean = True
# for col in STATUS_COLUMNS:
#     if col not in df.columns:
#         print(f"  ❌ MISSING COLUMN: {col}")
#         all_clean = False
#         continue
    
#     unique_vals = df[col].unique()
#     unexpected = [
#         v for v in unique_vals 
#         if str(v) not in ['Yes', 'No', 'Unknown']
#     ]
    
#     if unexpected:
#         print(f"  ❌ {col}: unexpected values → {unexpected}")
#         all_clean = False
#     else:
#         counts = df[col].value_counts().to_dict()
#         print(f"  ✅ {col}: {counts}")

# if all_clean:
#     print("\n✅ All status columns are clean")
# else:
#     print("\n❌ Fix the issues above before building")

# # ============================================
# # CHECK 3: Team and Stadium Names
# # ============================================
# print("\n=== TEAMS AND STADIUMS ===")
# for _, row in df.iterrows():
#     print(f"  {row['team_name']} → {row['stadium_name']}")

# # ============================================
# # CHECK 4: Missing Source URLs
# # ============================================
# print("\n=== SOURCE URLs ===")
# for _, row in df.iterrows():
#     url = row.get('source_url', '')
#     if pd.isna(url) or str(url).strip() == '':
#         print(f"  ❌ Missing URL: {row['team_name']}")
#     else:
#         print(f"  ✅ {row['team_name']}")

# # ============================================
# # CHECK 5: Completeness Score Per Team
# # ============================================
# print("\n=== COMPLETENESS SCORES ===")

# def completeness(row):
#     known = sum(
#         1 for col in STATUS_COLUMNS
#         if col in df.columns and row.get(col) in ['Yes', 'No']
#     )
#     return round((known / len(STATUS_COLUMNS)) * 100)

# df['completeness'] = df.apply(completeness, axis=1)

# for _, row in df.sort_values('completeness', ascending=False).iterrows():
#     bar = '█' * (row['completeness'] // 10) + '░' * (10 - row['completeness'] // 10)
#     print(f"  {bar} {row['completeness']:>3}%  {row['team_name']}")

# ============================================
# CHECK 6: Row and Column Count
# ============================================
print(f"\n=== SHAPE ===")
print(f"  Rows: {len(df)} (expected 16)")
print(f"  Columns: {len(df.columns)}")

# ============================================
# Check 7: Rename Columns for Consistency
# ============================================
print("\n=== RENAMING COLUMNS ===")
df.rename(columns={
    'videoboard_closded_captioning_information': 'videoboard_closed_captioning_information',
    'Guest Services Location': 'guest_services_location',
    'Interpretation_services_information': 'interpretation_services_information',
}, inplace=True)

# Verify
print([c for c in df.columns if c != c.lower() or ' ' in c])