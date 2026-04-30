import streamlit as st
import pandas as pd
import networkx as nx

# Import your custom modules
from graph_builder import (
    build_graph, get_all_teams, get_stadium_for_team, 
    get_stadiums_with_feature, FEATURE_DISPLAY_NAMES
)
from scoring import (
    calculate_score, grade_to_color, 
    get_grade_label
)

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="NWSL Accessibility Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DATA LOADING
# ============================================
@st.cache_resource
def load_data():
    """Loads datasets and builds the NetworkX graph."""
    try:
        # Load your updated dataset
        df_stadiums = pd.read_csv('data/nwsl_cleaned_new.csv')
        G = build_graph(df_stadiums)
    except FileNotFoundError:
        st.error("Stadium dataset 'data/nwsl_cleaned_new.csv' not found. Please ensure it is in the data folder.")
        G = nx.DiGraph()
        df_stadiums = pd.DataFrame()

    try:
        df_schedule = pd.read_csv('data/nwsl_schedule_2026.csv')
    except FileNotFoundError:
        st.warning("Schedule dataset 'data/nwsl_schedule_2026.csv' not found. Game browsing will be limited.")
        df_schedule = pd.DataFrame()

    return G, df_schedule, df_stadiums

G, df_schedule, df_stadiums = load_data()

if not G.nodes or df_stadiums.empty:
    st.stop()

# ============================================
# REUSABLE UI COMPONENTS
# ============================================
def render_stadium_details(stadium_name, team_name, venue_type=None, is_team_tab=False):
    """Renders the standard stadium detail view with grades, features, and detailed info."""
    
    # Extract the specific row for this stadium directly from our updated dataframe
    row = df_stadiums[(df_stadiums['stadium_name'] == stadium_name) & (df_stadiums['team_name'] == team_name)]
    if not row.empty:
        row = row.iloc[0]
    else:
        # Fallback if there's a mismatch (e.g. alternative venue)
        row = df_stadiums[df_stadiums['stadium_name'] == stadium_name].iloc[0]
    
    # 1 & 2: Header 2 Size Title with Stadium - Team format
    st.header(f"{stadium_name} - {team_name}")
    
    # 3: "About Me" Team Page Logic (Only triggers on Tab 2)
    if is_team_tab:
        col_text, col_logo = st.columns([3, 1])
        
        with col_logo:
            # Logo in the far right corner
            if pd.notna(row.get('team_logo')) and str(row.get('team_logo')).strip():
                st.image(row['team_logo'], width=150)
                
        with col_text:
            # City and State
            st.markdown(f"**📍 Location:** {row.get('city', 'Unknown')}, {row.get('state', 'Unknown')}")
            
            # Contact Information on its own line
            contact_parts = []
            if pd.notna(row.get('guest_services_email')) and str(row['guest_services_email']).strip():
                email = row['guest_services_email']
                contact_parts.append(f"✉️ [{email}](mailto:{email})")
                
            if pd.notna(row.get('guest_services_phone')) and str(row['guest_services_phone']).strip():
                contact_parts.append(f"📞 {row['guest_services_phone']}")
                
            if contact_parts:
                st.markdown("**Contact:** " + " | ".join(contact_parts))
                
            # Online Ticket Link
            if pd.notna(row.get('ticket_url')) and str(row['ticket_url']).strip():
                st.link_button("🎟️ Purchase Accessible Tickets", row['ticket_url'])
                
        st.divider()

    # FIFA Venue Messaging
    if venue_type == 'fifa_displaced':
        st.warning("🏟️ **Alternative Venue Alert:** This match is being played at an alternative venue due to the FIFA Men's World Cup. Accessibility features and policies may differ significantly from the team's primary stadium.")
    elif venue_type == 'special_event':
        st.info("🎟️ **Special Event Venue:** This match is being hosted at a special event venue. Standard accessibility rules for the home team may not apply.")

    stadium_score = calculate_score(G, stadium_name)
    
    if stadium_score['is_expansion']:
        st.info("🆕 **Expansion Team** — Detailed accessibility information for this stadium is currently pending.")
        return

    # Score Metrics
    m1, m2, m3 = st.columns(3)
    grade_emoji = grade_to_color(stadium_score['grade'])
    m1.metric("Overall Grade", f"{grade_emoji} {stadium_score['grade']}")
    m2.metric("Total Score", f"{stadium_score['total_score']} / 105")
    ada_text = "Yes" if stadium_score['ada_compliant'] else "No"
    m3.metric("ADA Compliant Baseline", ada_text)
    
    st.markdown(f"**Status:** *{get_grade_label(stadium_score['grade'])}*")
    
    # Feature Display Breakdown
    st.subheader("Accessibility Breakdown")
    breakdown = stadium_score['breakdown']
    tiers = [
        ("Tier 1: ADA Baseline", 'tier_1'),
        ("Tier 2: Extended Access", 'tier_2'),
        ("Tier 3: Inclusive Services", 'tier_3'),
        ("Bonus: Accessible Ticket Exchange", 'bonus')
    ]
    
    for tier_name, tier_key in tiers:
        if tier_key not in breakdown or not breakdown[tier_key]:
            continue
            
        tier_total = sum([v['earned'] for k, v in breakdown[tier_key].items()])
        tier_max = sum([v['possible'] for k, v in breakdown[tier_key].items()])
        
        with st.expander(f"{tier_name} ({tier_total}/{tier_max} pts)", expanded=False):
            for feature_key, details in breakdown[tier_key].items():
                feature_name = FEATURE_DISPLAY_NAMES.get(feature_key, feature_key)
                
                if details['status'] == 'Yes':
                    status_icon = "✅"
                elif details['status'] == 'No':
                    status_icon = "❌"
                else:
                    status_icon = "❓"
                
                st.markdown(f"**{status_icon} {feature_name}** ({details['earned']}/{details['possible']} pts)")
                
                # Show penalty conditions if they exist
                if details['condition_flag']:
                    st.warning(f"**{details['condition_flag']}:** {details['condition_text']}")

                # 4: Display specific information ONLY if the status is 'Yes'
                if details['status'] == 'Yes':
                    info_column = f"{feature_key}_information"
                    if info_column in row and pd.notna(row[info_column]) and str(row[info_column]).strip():
                        st.caption(f"📝 *{row[info_column]}*")
                
                st.divider()

    # 5: Guest Services Location Box (Below Tiered Info)
    if pd.notna(row.get('guest_services_location')) and str(row['guest_services_location']).strip():
        st.info(f"📍 **Guest Services Location:** {row['guest_services_location']}")

    # Policy Resource Link at the very bottom
    if pd.notna(row.get('source_url')) and str(row['source_url']).strip():
        st.markdown(f"[🔗 View Official Accessibility Policy]({row['source_url']})")

# ============================================
# SIDEBAR: METHODOLOGY
# ============================================
with st.sidebar:
    st.header("⚽ NWSL Access Hub")
    st.divider()
    st.subheader("📊 Scoring Methodology")
    st.markdown("""
    Stadiums are graded out of **105 possible points** using a tiered structure that penalizes barriers to access:
    
    * **Tier 1 (ADA Baseline - 40pts):** The legal minimums. Accessible seating, elevators, parking, and service animals. 
    * **Tier 2 (Extended - 35pts):** Wheelchair services, listening devices, closed captioning, gender-neutral restrooms.
    * **Tier 3 (Inclusive - 25pts):** Sensory accommodations, nursing rooms, interpretation services.
    * **Bonus (5pts):** Standard ticket exchanges for accessible seating.
    
    **Conditions & Penalties:** Features marked with a ⚠️ indicate that a service exists, but a barrier (like a 2-week advance notice requirement) limits its practical accessibility. These trigger point penalties.
    """)

# ============================================
# MAIN UI
# ============================================
st.title("🏟️ NWSL Accessibility Hub")
st.markdown("Plan your inclusive matchday experience by finding the accessibility services that meet your needs.")

tab1, tab2, tab3, tab4 = st.tabs(["📅 Browse by Game", "🛡️ Browse by Team", "🔍 Filter by Need", "📞 Guest Services Directory"])

# --------------------------------------------
# TAB 1: BROWSE BY GAME
# --------------------------------------------
with tab1:
    st.header("Matchday Accessibility")
    
    if not df_schedule.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            months = ["All Months"] + list(df_schedule['month'].dropna().unique())
            selected_month = st.selectbox("Filter by Month:", months)
            
            if selected_month != "All Months":
                filtered_schedule = df_schedule[df_schedule['month'] == selected_month]
            else:
                filtered_schedule = df_schedule
                
            selected_game_label = st.selectbox("Select a Match:", filtered_schedule['game_label'])
            
        with col2:
            if selected_game_label:
                game_row = filtered_schedule[filtered_schedule['game_label'] == selected_game_label].iloc[0]
                stadium_name = game_row['stadium']
                team_name = game_row['home_team']
                venue_type = game_row['venue_type']
                
                # is_team_tab=False keeps it clean for Matchday
                render_stadium_details(stadium_name, team_name, venue_type, is_team_tab=False)
    else:
        st.info("Schedule data is currently unavailable.")

# --------------------------------------------
# TAB 2: BROWSE BY TEAM
# --------------------------------------------
with tab2:
    st.header("Team Stadium Profiles")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        teams = get_all_teams(G)
        selected_team = st.selectbox("Choose an NWSL Team:", teams)
        selected_stadium = get_stadium_for_team(G, selected_team)
        
    with col2:
        if selected_stadium:
            # is_team_tab=True triggers the "About Me" layout
            render_stadium_details(selected_stadium, selected_team, venue_type=None, is_team_tab=True)

# --------------------------------------------
# TAB 3: FILTER BY NEED
# --------------------------------------------
with tab3:
    st.header("Search by Accessibility Need")
    st.markdown("Looking for a specific accommodation? Select a feature below to see which stadiums currently offer it.")
    
    display_to_key = {v: k for k, v in FEATURE_DISPLAY_NAMES.items()}
    selected_display_feature = st.selectbox("Select Accessibility Feature:", list(display_to_key.keys()))
    
    selected_feature_key = display_to_key[selected_display_feature]
    stadiums_with_feature = get_stadiums_with_feature(G, selected_feature_key, status='Yes')
    
    if stadiums_with_feature:
        st.success(f"Found {len(stadiums_with_feature)} stadium(s) with {selected_display_feature}:")
        for s in stadiums_with_feature:
            stadium_score = calculate_score(G, s)
            condition = None
            
            if not stadium_score.get('is_expansion'):
                for tier in ['tier_1', 'tier_2', 'tier_3', 'bonus']:
                    if selected_feature_key in stadium_score.get('breakdown', {}).get(tier, {}):
                        condition = stadium_score['breakdown'][tier][selected_feature_key].get('condition_flag')
            
            if condition:
                st.markdown(f"- **{s}** (⚠️ *{condition}*)")
            else:
                st.markdown(f"- **{s}**")
    else:
        st.info(f"No stadiums currently confirming {selected_display_feature}.")

# --------------------------------------------
# TAB 4: GUEST SERVICES DIRECTORY
# --------------------------------------------
with tab4:
    st.header("Guest Services Directory")
    st.markdown("Quickly find contact information and stadium locations for assistance on matchday.")
    
    # Rebuilding directory table using updated raw dataframe names
    contact_data = []
    for _, row in df_stadiums.iterrows():
        contact_data.append({
            "Team": row.get('team_name', ''),
            "Stadium": row.get('stadium_name', ''),
            "Phone": str(row.get('guest_services_phone', '')),
            "Email": str(row.get('guest_services_email', '')),
            "Location": str(row.get('guest_services_location', ''))
        })
        
    df_contacts = pd.DataFrame(contact_data)
    
    # Cleanup display
    df_contacts.replace('nan', '', inplace=True)
    df_contacts.replace('', 'Not Listed', inplace=True)
    
    st.dataframe(
        df_contacts,
        column_config={
            "Team": st.column_config.TextColumn("Team", width="medium"),
            "Stadium": st.column_config.TextColumn("Stadium", width="medium"),
            "Phone": st.column_config.TextColumn("Phone Number", width="medium"),
            "Email": st.column_config.TextColumn("Email Address", width="medium"),
            "Location": st.column_config.TextColumn("Physical Location", width="large")
        },
        hide_index=True,
        use_container_width=True
    )