# graph_builder.py
import networkx as nx
import pandas as pd

# ============================================
# DEFINE YOUR FEATURE COLUMNS
# These match your exact cleaned column names
# ============================================

STATUS_COLUMNS = [
    'accessible_seating',
    'accessible_seating_standard_ticket_exchange',
    'assisted_listening_devices',
    'videoboard_closed_captioning',
    'public_elevators',
    'wheelchair_services',
    'service_animals',
    'sensory_accommodations',
    'gender_neutral_restrooms',
    'parking_accessibility',
    'nursing_rooms',
    'interpretation_services',
]

INFO_COLUMNS = {
    'accessible_seating':                        'accessible_seating_information',
    'accessible_seating_standard_ticket_exchange': 'accessible_seating_information',
    'assisted_listening_devices':                'assisted_listening_devices_info',
    'videoboard_closed_captioning':              'videoboard_closed_captioning_information',
    'public_elevators':                          'public_elevators_information',
    'wheelchair_services':                       'wheelchair_services_information',
    'service_animals':                           'service_animals_information',
    'sensory_accommodations':                    'sensory_accommodations_information',
    'gender_neutral_restrooms':                  'gender_neutral_restrooms_information',
    'parking_accessibility':                     'parking_accessibility_information',
    'nursing_rooms':                             'nursing_rooms_information',
    'interpretation_services':                   'interpretation_services_information',
}

FEATURE_DISPLAY_NAMES = {
    'accessible_seating':                        'Accessible Seating',
    'accessible_seating_standard_ticket_exchange': 'Standard Ticket Exchange',
    'assisted_listening_devices':                'Assisted Listening Devices',
    'videoboard_closed_captioning':              'Closed Captioning',
    'public_elevators':                          'Public Elevators',
    'wheelchair_services':                       'Wheelchair Services',
    'service_animals':                           'Service Animals',
    'sensory_accommodations':                    'Sensory Accommodations',
    'gender_neutral_restrooms':                  'Gender Neutral Restrooms',
    'parking_accessibility':                     'Accessible Parking',
    'nursing_rooms':                             'Nursing Rooms',
    'interpretation_services':                   'Interpretation Services',
}

# ============================================
# BUILD THE GRAPH
# ============================================

def build_graph(df):
    """
    Builds a typed directed graph from the NWSL
    accessibility dataframe.

    Node types:
        Team              → NWSL team
        Stadium           → Physical venue
        AccessibilityFeature → Individual feature at a stadium
        PolicyPage        → Source URL for accessibility info

    Edge types:
        Team      → PLAYS_AT      → Stadium
        Stadium   → HAS_FEATURE   → AccessibilityFeature
        Stadium   → HAS_POLICY    → PolicyPage
    """

    G = nx.DiGraph()

    for _, row in df.iterrows():

        team    = row['team_name']
        stadium = row['stadium_name']
        url     = str(row.get('source_url', '')).strip()

        # ----------------------------------------
        # TEAM NODE
        # ----------------------------------------
        G.add_node(
            team,
            node_type = 'Team',
            city      = row.get('city', 'Unknown'),
            state     = row.get('state', 'Unknown'),
        )

        # ----------------------------------------
        # STADIUM NODE
        # ----------------------------------------
        
        # Determine data completeness for this stadium
        known = sum(
            1 for col in STATUS_COLUMNS
            if row.get(col) in ['Yes', 'No']
        )
        completeness = round((known / len(STATUS_COLUMNS)) * 100)

        # Flag expansion teams
        is_expansion = completeness <= 10

        G.add_node(
            stadium,
            node_type    = 'Stadium',
            team         = team,
            city         = row.get('city', 'Unknown'),
            state        = row.get('state', 'Unknown'),
            completeness = completeness,
            is_expansion = is_expansion,
            guest_services_contact  = str(row.get('guest_services_contact', '')).strip(),
            guest_services_location = str(row.get('guest_services_location', '')).strip(),
        )

        # ----------------------------------------
        # POLICY PAGE NODE
        # ----------------------------------------
        if url and url != 'nan':
            G.add_node(
                url,
                node_type = 'PolicyPage',
                team      = team,
                stadium   = stadium,
            )
            G.add_edge(
                stadium, url,
                relationship = 'HAS_POLICY'
            )

        # ----------------------------------------
        # TEAM → STADIUM EDGE
        # ----------------------------------------
        G.add_edge(
            team, stadium,
            relationship = 'PLAYS_AT'
        )

        # ----------------------------------------
        # ACCESSIBILITY FEATURE NODES AND EDGES
        # ----------------------------------------
        for col in STATUS_COLUMNS:
            status       = row.get(col, 'Unknown')
            display_name = FEATURE_DISPLAY_NAMES.get(col, col)
            info_col     = INFO_COLUMNS.get(col, '')
            info_text    = str(row.get(info_col, '')).strip() if info_col else ''

            # Clean up empty or NaN info text
            if not info_text or info_text.lower() in ['nan', 'none', '']:
                info_text = 'Contact stadium for more information.'

            # Unique ID for this feature at this stadium
            feature_id = f"{stadium}::{col}"

            G.add_node(
                feature_id,
                node_type    = 'AccessibilityFeature',
                feature_name = display_name,
                feature_key  = col,
                status       = status,
                info         = info_text,
                stadium      = stadium,
                team         = team,
            )

            G.add_edge(
                stadium, feature_id,
                relationship = 'HAS_FEATURE',
                feature_key  = col,
                status       = status,
            )

    return G


# ============================================
# QUERY FUNCTIONS
# These are what your app.py will call
# ============================================

def get_stadium_for_team(G, team_name):
    """
    Returns the stadium name for a given team.
    """
    for successor in G.successors(team_name):
        if G.nodes[successor].get('node_type') == 'Stadium':
            return successor
    return None


def get_features_for_stadium(G, stadium_name):
    """
    Returns a list of all accessibility feature
    nodes for a given stadium.

    Each item in the list is a dict with:
        feature_name, feature_key, status, info
    """
    features = []
    for successor in G.successors(stadium_name):
        node = G.nodes[successor]
        if node.get('node_type') == 'AccessibilityFeature':
            features.append({
                'feature_name': node.get('feature_name'),
                'feature_key':  node.get('feature_key'),
                'status':       node.get('status'),
                'info':         node.get('info'),
                'stadium':      node.get('stadium'),
                'team':         node.get('team'),
            })
    return features


def get_policy_url_for_stadium(G, stadium_name):
    """
    Returns the source URL for a stadium's
    accessibility policy page.
    """
    for successor in G.successors(stadium_name):
        node = G.nodes[successor]
        if node.get('node_type') == 'PolicyPage':
            return successor
    return None


def get_stadiums_with_feature(G, feature_key, status='Yes'):
    """
    Returns a list of stadium names that have
    a specific feature confirmed.

    Use this for the sidebar filter:
    'Show me all stadiums with a sensory room'
    """
    results = []
    for node_id, node_data in G.nodes(data=True):
        if (node_data.get('node_type') == 'AccessibilityFeature'
                and node_data.get('feature_key') == feature_key
                and node_data.get('status') == status):
            results.append(node_data.get('stadium'))
    return results


def get_all_teams(G):
    """
    Returns a sorted list of all team names.
    """
    return sorted([
        n for n, d in G.nodes(data=True)
        if d.get('node_type') == 'Team'
    ])


def get_all_stadiums(G):
    """
    Returns a sorted list of all stadium names.
    """
    return sorted([
        n for n, d in G.nodes(data=True)
        if d.get('node_type') == 'Stadium'
    ])


def get_stadium_data(G, stadium_name):
    """
    Returns the full node data dict for a stadium.
    """
    if stadium_name in G.nodes:
        return G.nodes[stadium_name]
    return None


def get_team_data(G, team_name):
    """
    Returns the full node data dict for a team.
    """
    if team_name in G.nodes:
        return G.nodes[team_name]
    return None


# ============================================
# VERIFY THE GRAPH BUILT CORRECTLY
# Run this file directly to test:
# python graph_builder.py
# ============================================

if __name__ == '__main__':
    df = pd.read_csv('nwsl_stadium_cleaned.csv')
    G  = build_graph(df)

    print("=== GRAPH SUMMARY ===")
    print(f"Total nodes : {G.number_of_nodes()}")
    print(f"Total edges : {G.number_of_edges()}")

    teams    = get_all_teams(G)
    stadiums = get_all_stadiums(G)
    print(f"Team nodes  : {len(teams)}")
    print(f"Stadium nodes: {len(stadiums)}")

    print("\n=== SAMPLE: Kansas City Current ===")
    stadium = get_stadium_for_team(G, 'Kansas City Current')
    print(f"Stadium     : {stadium}")
    print(f"Policy URL  : {get_policy_url_for_stadium(G, stadium)}")

    features = get_features_for_stadium(G, stadium)
    print(f"Features    : {len(features)}")
    for f in features:
        print(f"  {f['status']:>7}  {f['feature_name']}")

    print("\n=== STADIUMS WITH SENSORY ACCOMMODATIONS ===")
    sensory = get_stadiums_with_feature(G, 'sensory_accommodations')
    for s in sensory:
        print(f"  ✅ {s}")

    print("\n=== STADIUMS WITH INTERPRETATION SERVICES ===")
    interp = get_stadiums_with_feature(G, 'interpretation_services')
    for s in interp:
        print(f"  ✅ {s}")