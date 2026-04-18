"""
Employee Assignment Service.

Maps task intents to the appropriate internal team.
Simple and deliberate — a more complex load-balancing assignment
system was considered but excluded as over-engineering for this stage.
"""


INTENT_TO_TEAM = {
    'send_money': 'Finance',
    'verify_document': 'Legal',
    'hire_service': 'Operations',
    'get_airport_transfer': 'Operations',
    'check_status': 'Support',
    'unknown': 'Support',
}

TEAM_DESCRIPTIONS = {
    'Finance': 'Handles all money transfers, payment verification, and AML compliance.',
    'Legal': 'Handles document verification, land searches, and legal compliance.',
    'Operations': 'Handles service hires, airport transfers, and on-ground logistics.',
    'Support': 'Handles customer queries, status checks, and escalations.',
}


def assign_team(intent: str) -> str:
    """Returns the team name responsible for the given intent."""
    return INTENT_TO_TEAM.get(intent, 'Support')


def get_team_description(team: str) -> str:
    """Returns a human-readable description of the team's responsibilities."""
    return TEAM_DESCRIPTIONS.get(team, 'General support team.')
