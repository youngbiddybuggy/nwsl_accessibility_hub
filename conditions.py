# conditions.py
# ============================================
# MANUAL CONDITION FLAGS
# 
# Used to flag accessibility features
# that are technically available but have
# barriers, restrictions, or conditions that
# reduce their accessibility in practice.
#
# penalty values:
#   0.25 = minor condition (advance notice required)
#   0.50 = moderate condition (significant barrier)
#   0.75 = major condition (severely limited access)
#
# Structure:
# CONDITIONS = {
#     'Stadium Name': {
#         'feature_key': {
#             'penalty':     float,
#             'condition':   str,
#             'flag':        str,
#         }
#     }
# }
# ============================================

CONDITIONS = {

    'PayPal Park': {
        'service_animals': {
            'penalty':   0.25,
            'condition': 'Service animals in training require '
                         'advance authorization via text to '
                         '408-909-4625 at least one day before '
                         'the match.',
            'flag':      '⚠️ Advance Notice Required',
        },
        'accessible_seating': {
            'penalty':   0.25,
            'condition': 'Accessible seating is available but must be purchased by contacting the box office directly. This may create barriers for some fans.',
            'flag':      '⚠️ Must Contact Box Office',
        },
    },

    'America First Field': {
        'wheelchair_services': {
            'penalty':   0.75,
            'condition': 'America First Field does not lend or '
                         'rent wheelchairs to patrons for any '
                         'events.',
            'flag':      '⚠️ Service Not Available',
        },
        'gender_neutral_restrooms': {
            'penalty':   0.25,
            'condition': 'There is one Family/Gender-neutral restrooms  available at America First Field which may lead to longer wait times and limited access for those who need it.',
            'flag':      '⚠️ Limited Availability',
        },
    },

    'BMO Stadium': {
        'interpretation_services': {
            'penalty':   0.25,
            'condition': 'Interpretation services must be '
                         'requested at least two weeks in '
                         'advance. Availability is not '
                         'guaranteed.',
            'flag':      '⚠️ Must Request 2 Weeks in Advance',
        },
        
    },
    'Snapdragon Stadium': {
        'accessible_seating': {
            'penalty':   0.25,
            'condition': 'Accessible seating is available but must be purchased by contacting the box office directly. This may create barriers for some fans.',
            'flag':      '⚠️ Must Contact Box Office',
        },
    },

    'CPKC Stadium': {
        'interpretation_services': {
            'penalty':   0.25,
            'condition': 'Sign language services are available '
                         'by request no later than 72 hours '
                         'prior to the event.',
            'flag':      '⚠️ Must Request 72 Hours in Advance',
        },
        'public_elevators': {'penalty': 0.25,
                             'condition': 'There is currently one public elevator available at CPKC Stadium, which may lead to longer wait times and limited access during peak periods.',
                             'flag': '⚠️ Limited Elevator Access'},
    },
    

    'Gillette Stadium': {
        'accessible_seating': {
            'penalty':   0.50,
            'condition': 'Boston Legacy FC is a new expansion '
                         'team for 2025. Accessibility '
                         'information is not yet publicly '
                         'available.',
            'flag':      '🆕 Expansion Team - Data Pending',
        },
    },
    'Providence Park': {
    'parking_accessibility': {
        'penalty':   0.0,       
        'condition': 'Providence Park has no on-site or nearby '
                     'accessible parking due to its urban location. '
                     'The stadium recommends public transit. '
                     'This reflects city infrastructure, not '
                     'stadium policy.',
        'flag':      'ℹ️ No Nearby Parking — Urban Stadium',
    },
},

    'Centennial Stadium': {
        'accessible_seating': {
            'penalty':   0.50,
            'condition': 'Denver Summit FC is a new expansion '
                         'team for 2025. Accessibility '
                         'information is not yet publicly '
                         'available.',
            'flag':      '🆕 Expansion Team - Data Pending',
        },
    },

    

}


def get_condition(stadium_name, feature_key):
    """
    Returns the condition dict for a stadium/feature
    combination, or None if no condition exists.
    """
    return (CONDITIONS
            .get(stadium_name, {})
            .get(feature_key, None))


def get_all_conditions_for_stadium(stadium_name):
    """
    Returns all condition flags for a given stadium.
    Use this to display warnings in the app.
    """
    return CONDITIONS.get(stadium_name, {})


def has_condition(stadium_name, feature_key):
    """
    Returns True if a condition flag exists for
    this stadium/feature combination.
    """
    return get_condition(stadium_name, feature_key) is not None
