"""
Risk Scoring Service for Vunoh Global.

Calculates a risk score (0-100) for each task based on factors grounded in
real Kenyan diaspora fraud and service failure patterns.

Design decisions:
- Urgency + large amounts are weighted heavily (wire fraud pattern)
- Land title verification is the highest-risk document type in Kenya
  (land fraud is among the most common financial crimes in Kenya)
- Unknown recipients increase risk on money transfers
- Scores are additive with a hard cap at 100
"""

import logging

logger = logging.getLogger(__name__)


def calculate_risk(intent: str, entities: dict) -> dict:
    """
    Calculate a risk score and return a dict with:
    - score: int 0-100
    - level: 'low' | 'medium' | 'high'
    - reasons: list of strings explaining what contributed to the score
    """
    score = 0
    reasons = []

    urgency = entities.get('urgency', False)
    amount = entities.get('amount') or 0
    recipient_name = entities.get('recipient_name')
    recipient_phone = entities.get('recipient_phone')
    document_type = entities.get('document_type', '') or ''
    service_type = entities.get('service_type', '') or ''
    location = entities.get('location', '') or ''

    # ── URGENCY (applies to all intents) ──────────────────────
    if urgency:
        score += 20
        reasons.append("Urgency flag: customer marked request as urgent (+20). "
                       "Urgency is a common trigger in diaspora wire fraud.")

    # ── MONEY TRANSFER RULES ──────────────────────────────────
    if intent == 'send_money':
        if amount >= 100_000:
            score += 30
            reasons.append(f"Very large transfer amount: KES {amount:,} (+30). "
                           "Transfers above KES 100k require enhanced due diligence.")
        elif amount >= 50_000:
            score += 20
            reasons.append(f"Large transfer amount: KES {amount:,} (+20). "
                           "Transfers above KES 50k carry elevated fraud risk.")
        elif amount >= 10_000:
            score += 10
            reasons.append(f"Moderate transfer amount: KES {amount:,} (+10).")

        if not recipient_name and not recipient_phone:
            score += 25
            reasons.append("Unknown recipient: no name or phone provided (+25). "
                           "Unverified recipients significantly increase fraud risk.")
        elif not recipient_phone:
            score += 10
            reasons.append("No recipient phone number provided (+10).")

        if urgency and amount >= 50_000:
            score += 15
            reasons.append("Urgency + large amount combination (+15 bonus). "
                           "This combination is the most common pattern in overseas wire fraud.")

    # ── DOCUMENT VERIFICATION RULES ───────────────────────────
    elif intent == 'verify_document':
        doc_lower = document_type.lower()
        if any(w in doc_lower for w in ['land', 'title', 'deed', 'plot', 'parcel']):
            score += 30
            reasons.append("Land title verification (+30). "
                           "Land fraud is among the most prevalent financial crimes in Kenya. "
                           "Title deed forgery is widespread.")
        elif any(w in doc_lower for w in ['logbook', 'vehicle', 'car']):
            score += 20
            reasons.append("Vehicle logbook verification (+20). Vehicle fraud is common.")
        elif any(w in doc_lower for w in ['id', 'passport', 'huduma', 'kra']):
            score += 15
            reasons.append("Identity document verification (+15). ID fraud risk.")
        else:
            score += 10
            reasons.append(f"General document verification (+10): {document_type or 'unspecified'}.")

    # ── SERVICE HIRE RULES ────────────────────────────────────
    elif intent == 'hire_service':
        unverified_areas = ['unknown', 'rural', 'village', 'upcountry']
        if any(area in location.lower() for area in unverified_areas):
            score += 15
            reasons.append("Service requested in area outside verified provider network (+15).")
        else:
            score += 5
            reasons.append("Service hire: standard operational risk (+5).")

        high_risk_services = ['lawyer', 'wakili', 'legal', 'notary', 'advocate']
        if any(s in service_type.lower() for s in high_risk_services):
            score += 10
            reasons.append("Legal service hire (+10): requires credential verification.")

    # ── AIRPORT TRANSFER ──────────────────────────────────────
    elif intent == 'get_airport_transfer':
        score += 5
        reasons.append("Airport transfer: low base risk (+5).")

    # ── CHECK STATUS ──────────────────────────────────────────
    elif intent == 'check_status':
        score = 0
        reasons.append("Status check request: no risk score applicable.")

    # ── CAP AT 100 ────────────────────────────────────────────
    score = min(score, 100)

    level = 'low'
    if score >= 70:
        level = 'high'
    elif score >= 40:
        level = 'medium'

    logger.info(f"Risk scoring complete: score={score}, level={level}, factors={len(reasons)}")

    return {
        'score': score,
        'level': level,
        'reasons': reasons
    }
