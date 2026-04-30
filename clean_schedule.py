# clean_schedule.py
import pandas as pd

# ============================================
# LOAD
# ============================================

RAW_PATH   = 'data/nwsl_schedule_raw.csv'
CLEAN_PATH = 'data/nwsl_schedule_2026.csv'

df = pd.read_csv(RAW_PATH)

# ============================================
# PREVIEW
# ============================================

print("=== RAW COLUMNS ===")
print(df.columns.tolist())

print("\n=== SAMPLE RAW DATA ===")
print(df.head(3).to_string())

# ============================================
# RENAME COLUMNS
# ============================================

df.rename(columns={'week_match_up': 'matchday'}, inplace=True)

# ============================================
# APPLY NAME MAPPINGS BEFORE ANYTHING ELSE
# ============================================

TEAM_NAME_MAP = {
    'Angel City':        'Angel City FC',
    'Bay':               'Bay FC',
    'Boston Legacy':     'Boston Legacy FC',
    'Chicago Stars':     'Chicago Stars FC',
    'Denver Summit':     'Denver Summit FC',
    'Gotham FC':         'NJ/NY Gotham FC',
    'Portland Thorns':   'Portland Thorns FC',
    'Racing Louisville': 'Racing Louisville FC',
    'San Diego Wave':    'San Diego Wave FC',
    'Seattle Reign':     'Seattle Reign FC',
    'Utah Royals':       'Utah Royals FC',
}

STADIUM_NAME_MAP = {
    'Inter&Co Stadium':                              'INTER&Co Stadium',
    'Northwestern Medicine Field at Martin Stadium': 'Northwestern Martin Stadium (temporary)',
    'Sports Illustrated Stadium':                    'Red Bull Arena',
}

df['home_team'] = df['home_team'].replace(TEAM_NAME_MAP)
df['away_team'] = df['away_team'].replace(TEAM_NAME_MAP)
df['stadium']   = df['stadium'].replace(STADIUM_NAME_MAP)

# ============================================
# PARSE DATE COLUMN
# Input format: 14/03/2026 16:30
# ============================================

df['datetime_parsed'] = pd.to_datetime(
    df['date'],
    format='%d/%m/%Y %H:%M',
    errors='coerce'
)

failed = df[df['datetime_parsed'].isna()]
if not failed.empty:
    print(f"\n⚠️  {len(failed)} rows failed to parse:")
    print(failed[['date', 'home_team', 'away_team']].to_string())
else:
    print("\n✅ All dates parsed successfully")

# ============================================
# BUILD CLEAN COLUMNS
# ============================================

def format_time(dt):
    if pd.isna(dt):
        return 'TBD'
    return dt.strftime('%I:%M %p').lstrip('0')

def format_date_display(dt):
    if pd.isna(dt):
        return 'TBD'
    return dt.strftime('%B %d, %Y')

def format_date_sort(dt):
    if pd.isna(dt):
        return '9999-99-99'
    return dt.strftime('%Y-%m-%d')

df['date_display'] = df['datetime_parsed'].apply(format_date_display)
df['time_et']      = df['datetime_parsed'].apply(format_time)
df['day_of_week']  = df['datetime_parsed'].dt.strftime('%A')
df['month']        = df['datetime_parsed'].dt.strftime('%B')
df['date_sort']    = df['datetime_parsed'].apply(format_date_sort)

# ============================================
# CLASSIFY VENUE TYPES
# ============================================

FIFA_DISPLACED_VENUES = {
    'Citi Field',
    'Centreville Bank Stadium',
    "Dick's Sporting Goods Park",
    'Icahn Stadium',
    'One Spokane Stadium',
}

SPECIAL_EVENT_VENUES = {
    'Empower Field at Mile High',
}

UNKNOWN_VENUES = {
    'TBA',
}

def classify_venue(stadium):
    if stadium in FIFA_DISPLACED_VENUES:
        return 'fifa_displaced'
    elif stadium in SPECIAL_EVENT_VENUES:
        return 'special_event'
    elif stadium in UNKNOWN_VENUES:
        return 'tba'
    else:
        return 'home_venue'

df['venue_type'] = df['stadium'].apply(classify_venue)

# ============================================
# BUILD GAME LABEL
# ============================================

def build_game_label(row):
    if row['date_display'] == 'TBD':
        return f"TBD — {row['home_team']} vs {row['away_team']}"
    return (
        f"{row['date_display']}  {row['time_et']}  —  "
        f"{row['home_team']} vs {row['away_team']}"
    )

df['game_label'] = df.apply(build_game_label, axis=1)

# ============================================
# VALIDATE
# ============================================

KNOWN_STADIUMS = [
    'BMO Stadium',
    'PayPal Park',
    'Northwestern Martin Stadium (temporary)',
    'Shell Energy Stadium',
    'CPKC Stadium',
    'Red Bull Arena',
    'First Horizon Stadium at WakeMed Soccer Park',
    'Lumen Field',
    'INTER&Co Stadium',
    'Providence Park',
    'Lynn Family Stadium',
    'Snapdragon Stadium',
    'America First Field',
    'Audi Field',
    'Gillette Stadium',
    'Centennial Stadium',
]

KNOWN_TEAMS = [
    'Angel City FC', 'Bay FC', 'Boston Legacy FC',
    'Chicago Stars FC', 'Houston Dash', 'Kansas City Current',
    'NJ/NY Gotham FC', 'North Carolina Courage', 'Seattle Reign FC',
    'Orlando Pride', 'Portland Thorns FC', 'Racing Louisville FC',
    'San Diego Wave FC', 'Utah Royals FC', 'Washington Spirit',
    'Denver Summit FC',
]

print("\n=== STADIUM VALIDATION ===")
for _, row in df.iterrows():
    stadium    = row['stadium']
    venue_type = row['venue_type']

    if venue_type == 'home_venue' and stadium not in KNOWN_STADIUMS:
        print(f"  ❌ MISMATCH: '{stadium}' — not in accessibility CSV")
    elif venue_type == 'fifa_displaced':
        print(f"  ⚽ FIFA venue: '{stadium}'")
    elif venue_type == 'special_event':
        print(f"  🏟️  Special event: '{stadium}'")
    elif venue_type == 'tba':
        print(f"  📅 TBA: '{stadium}'")
    else:
        print(f"  ✅ {stadium}")

print("\n=== TEAM VALIDATION ===")
all_teams   = set(df['home_team'].tolist() + df['away_team'].tolist())
team_errors = []

for team in sorted(all_teams):
    if team in KNOWN_TEAMS:
        print(f"  ✅ {team}")
    else:
        print(f"  ❌ MISMATCH: '{team}'")
        team_errors.append(team)

print("\n=== VALIDATION SUMMARY ===")
if team_errors:
    print(f"  ❌ {len(team_errors)} team mismatches remaining")
    for t in team_errors:
        print(f"     → '{t}'")
else:
    print("  ✅ All team names clean")

# ============================================
# DROP WORKING COLUMNS AND SAVE
# ============================================

df.drop(columns=['datetime_parsed'], inplace=True)

df.sort_values('date_sort', inplace=True)
df.reset_index(drop=True, inplace=True)

df = df[[
    'matchday',
    'date',
    'date_display',
    'time_et',
    'day_of_week',
    'month',
    'date_sort',
    'home_team',
    'away_team',
    'stadium',
    'venue_type',
    'game_label',
]]

df.to_csv(CLEAN_PATH, index=False)

print(f"\n=== SAVED ===")
print(f"  {len(df)} games written to {CLEAN_PATH}")
print(f"  Matchdays: {df['matchday'].nunique()}")
print(f"  Date range: {df['date_sort'].min()} to {df['date_sort'].max()}")

print("\n=== SAMPLE CLEAN OUTPUT ===")
print(df[['game_label', 'time_et', 'day_of_week', 'matchday']].head(5).to_string())