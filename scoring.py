# scoring.py
from conditions import get_condition
from graph_builder import get_features_for_stadium

# ============================================
# SCORING WEIGHTS BY TIER
# ============================================

TIER_1_ADA_BASELINE = {
    'accessible_seating':    10,
    'public_elevators':      10,
    'parking_accessibility': 10,
    'service_animals':       10,
}

TIER_2_EXTENDED = {
    'wheelchair_services':          10,
    'assisted_listening_devices':   10,
    'videoboard_closed_captioning':  8,
    'gender_neutral_restrooms':      7,
}

TIER_3_INCLUSIVE = {
    'sensory_accommodations':  10,
    'nursing_rooms':            8,
    'interpretation_services':  7,
}

BONUS = {
    'accessible_seating_standard_ticket_exchange': 3,
}

UNKNOWN_PARTIAL = 0.20

MAX_BASE_SCORE = (
    sum(TIER_1_ADA_BASELINE.values()) +
    sum(TIER_2_EXTENDED.values()) +
    sum(TIER_3_INCLUSIVE.values())
)  # = 100

EXPANSION_TEAMS = {
    'Gillette Stadium',
    'Centennial Stadium',
}

GRADE_LABELS = {
    'A':   'Exceptional Accessibility',
    'B':   'Above Average',
    'C':   'Meets Baseline',
    'D':   'Below Baseline — Notable Gaps',
    'F':   'Significant Accessibility Gaps',
    'N/A': 'Expansion Team — Data Pending',
}


# ============================================
# GRADE CONVERSION — defined first
# ============================================

def score_to_grade(score):
    if score >= 90:   return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else:             return 'F'


def grade_to_color(grade):
    return {
        'A':   '🟢',
        'B':   '🔵',
        'C':   '🟡',
        'D':   '🟠',
        'F':   '🔴',
        'N/A': '⚪',
    }.get(grade, '⚪')


def get_grade_label(grade):
    return GRADE_LABELS.get(grade, '')


def grade_to_streamlit_color(grade):
    return {
        'A':   'green',
        'B':   'blue',
        'C':   'orange',
        'D':   'orange',
        'F':   'red',
        'N/A': 'gray',
    }.get(grade, 'gray')


# ============================================
# FEATURE SCORING WITH CONDITION SUPPORT
# ============================================

def score_feature_with_detail(feature_key, max_points, stadium_name, feature_status):
    """
    Scores a single feature and returns full detail
    including any condition penalty applied.
    """
    status    = feature_status.get(feature_key, 'Unknown')
    condition = get_condition(stadium_name, feature_key)

    if status == 'Yes':
        base = max_points
    elif status == 'No':
        base = 0
    else:
        base = round(max_points * UNKNOWN_PARTIAL)

    if condition and status == 'Yes':
        penalty        = condition['penalty']
        earned         = round(base * (1 - penalty))
        condition_flag = condition['flag']
        condition_text = condition['condition']
    else:
        earned         = base
        penalty        = 0
        condition_flag = None
        condition_text = None

    return {
        'status':         status,
        'earned':         earned,
        'possible':       max_points,
        'penalty':        penalty,
        'condition_flag': condition_flag,
        'condition_text': condition_text,
    }


# ============================================
# CALCULATE FULL STADIUM SCORE
# ============================================

def calculate_score(G, stadium_name):
    """
    Returns a detailed scoring breakdown for a stadium.
    """
    if stadium_name in EXPANSION_TEAMS:
        return {
            'stadium':       stadium_name,
            'total_score':   None,
            'grade':         'N/A',
            'ada_compliant': None,
            'is_expansion':  True,
            'breakdown':     {},
            'tier_1_score':  None,
            'tier_1_max':    40,
            'tier_2_score':  None,
            'tier_2_max':    35,
            'tier_3_score':  None,
            'tier_3_max':    25,
            'bonus_score':   None,
        }

    features = get_features_for_stadium(G, stadium_name)

    feature_status = {
        f['feature_key']: f['status']
        for f in features
    }

    breakdown = {
        'tier_1': {},
        'tier_2': {},
        'tier_3': {},
        'bonus':  {},
    }

    for key, points in TIER_1_ADA_BASELINE.items():
        breakdown['tier_1'][key] = score_feature_with_detail(
            key, points, stadium_name, feature_status
        )

    for key, points in TIER_2_EXTENDED.items():
        breakdown['tier_2'][key] = score_feature_with_detail(
            key, points, stadium_name, feature_status
        )

    for key, points in TIER_3_INCLUSIVE.items():
        breakdown['tier_3'][key] = score_feature_with_detail(
            key, points, stadium_name, feature_status
        )

    for key, points in BONUS.items():
        breakdown['bonus'][key] = score_feature_with_detail(
            key, points, stadium_name, feature_status
        )

    tier_1_score = sum(v['earned'] for v in breakdown['tier_1'].values())
    tier_2_score = sum(v['earned'] for v in breakdown['tier_2'].values())
    tier_3_score = sum(v['earned'] for v in breakdown['tier_3'].values())
    bonus_score  = sum(v['earned'] for v in breakdown['bonus'].values())

    base_score  = tier_1_score + tier_2_score + tier_3_score
    total_score = min(base_score + bonus_score, 105)

    return {
        'stadium':       stadium_name,
        'total_score':   total_score,
        'base_score':    base_score,
        'tier_1_score':  tier_1_score,
        'tier_1_max':    40,
        'tier_2_score':  tier_2_score,
        'tier_2_max':    35,
        'tier_3_score':  tier_3_score,
        'tier_3_max':    25,
        'bonus_score':   bonus_score,
        'grade':         score_to_grade(total_score),
        'ada_compliant': tier_1_score >= 32,
        'is_expansion':  False,
        'breakdown':     breakdown,
    }


# ============================================
# CONVENIENCE FUNCTIONS FOR APP.PY
# ============================================

def get_grade(G, stadium_name):
    return calculate_score(G, stadium_name)['grade']


def get_all_scores(G):
    from graph_builder import get_all_stadiums
    stadiums = get_all_stadiums(G)
    scores   = [calculate_score(G, s) for s in stadiums]

    graded   = [s for s in scores if s['grade'] != 'N/A']
    ungraded = [s for s in scores if s['grade'] == 'N/A']

    graded_sorted = sorted(
        graded,
        key=lambda x: x['total_score'],
        reverse=True
    )

    return graded_sorted + ungraded


def get_tier_summary(score_result):
    if score_result.get('grade') == 'N/A':
        return {
            'ADA Baseline':       'N/A',
            'Extended Access':    'N/A',
            'Inclusive Services': 'N/A',
        }
    return {
        'ADA Baseline':       f"{score_result['tier_1_score']}/40",
        'Extended Access':    f"{score_result['tier_2_score']}/35",
        'Inclusive Services': f"{score_result['tier_3_score']}/25",
    }


# ============================================
# TEST
# python scoring.py
# ============================================

if __name__ == '__main__':
    import pandas as pd
    from graph_builder import build_graph

    df = pd.read_csv('data/nwsl_cleaned_new.csv')
    G  = build_graph(df)

    print("=== ALL STADIUM SCORES ===")
    all_scores = get_all_scores(G)

    for result in all_scores:
        emoji = grade_to_color(result['grade'])

        if result['grade'] == 'N/A':
            print(
                f"  {emoji} N/A  {'---':>3}       "
                f"{result['stadium']:<45}  "
                f"Expansion Team — Data Pending"
            )
            continue

        ada_flag = '⚠️  ADA Gap' if not result['ada_compliant'] else ''
        print(
            f"  {emoji} {result['grade']}  "
            f"{result['total_score']:>3}"
            f"{result['stadium']:<45}  "
            f"T1:{result['tier_1_score']}/40  "
            f"T2:{result['tier_2_score']}/35  "
            f"T3:{result['tier_3_score']}/25  "
            f"{ada_flag}"
        )

    print(f"\n=== DETAILED: Kansas City Current ===")
    result = calculate_score(G, 'CPKC Stadium')
    print(f"Grade: {result['grade']}  Score: {result['total_score']}")
    print(f"ADA Compliant: {result['ada_compliant']}")

    for tier_name, tier_key in [
        ("Tier 1 — ADA Baseline",    'tier_1'),
        ("Tier 2 — Extended Access", 'tier_2'),
        ("Tier 3 — Inclusive",       'tier_3'),
        ("Bonus",                    'bonus'),
    ]:
        print(f"\n{tier_name}:")
        for k, v in result['breakdown'][tier_key].items():
            flag = f"  {v['condition_flag']}" if v['condition_flag'] else ''
            print(
                f"  {v['status']:>7}  "
                f"{v['earned']:>2}/{v['possible']}  "
                f"{k}{flag}"
            )
