"""
AI Service — handles all calls to Google Gemini.

This module is the brain of the application. It:
1. Extracts intent and entities from customer messages
2. Generates fulfilment steps
3. Produces WhatsApp, Email, and SMS confirmation messages
"""

import json
import re
import logging
from django.conf import settings
from typing import Union

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# SYSTEM PROMPT — carefully engineered for
# structured, parseable, Kenyan-context output
# ─────────────────────────────────────────────
EXTRACTION_SYSTEM_PROMPT = """
You are a structured data extraction engine for Vunoh Global, a platform that helps Kenyans 
living abroad manage tasks back home in Kenya.

Your ONLY job is to analyse a customer's plain-English message and return a valid JSON object.
Do NOT add any explanation, markdown, code fences, or preamble. Return raw JSON only.

=== KENYA CONTEXT ===
- Common cities: Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, Thika, Nyeri, Machakos, Kitale
- Common money transfer: M-Pesa, bank transfer, Western Union equivalent
- Common documents: title deed, land title, Huduma Namba, KRA PIN, ID, certificate, logbook
- Common services: cleaner (msafi/safisha), lawyer (wakili), errand runner (mtumishi), 
  mechanic (fundi), caretaker (caretaker/msimamizi), driver, nurse/carer
- Currency: KES (Kenyan Shillings). Convert if another currency is mentioned.

=== INTENT DEFINITIONS ===
- send_money: customer wants to transfer money to someone in Kenya
- hire_service: customer wants to hire a person or company to do something in Kenya
- verify_document: customer wants a document verified, checked, or processed
- get_airport_transfer: customer needs a ride or pickup at a Kenyan airport
- check_status: customer is asking about an existing task

=== OUTPUT SCHEMA — return exactly this structure ===
{
  "intent": "<one of the five intents above>",
  "confidence": <0.0 to 1.0, how certain you are of the intent>,
  "entities": {
    "amount": <number or null — amount in KES>,
    "recipient_name": "<string or null>",
    "recipient_phone": "<string or null>",
    "recipient_relationship": "<e.g. mother, friend, landlord, or null>",
    "location": "<city, estate, or area in Kenya, or null>",
    "service_type": "<type of service or null>",
    "document_type": "<type of document or null>",
    "urgency": <true or false>,
    "urgency_reason": "<why it is urgent, or null>",
    "scheduled_date": "<date string if mentioned, or null>",
    "additional_notes": "<any other relevant detail, or null>"
  },
  "summary": "<one sentence plain-English summary of the request>"
}

=== RULES ===
1. urgency is TRUE if the message contains words like: urgent, ASAP, today, immediately, 
   emergency, right now, tonight, this morning
2. If an amount is mentioned in USD, multiply by 130 to convert to KES
3. If recipient relationship is not mentioned, set to null — do NOT guess
4. Return ONLY the JSON object. No markdown. No explanation. No ```json fences.
"""

STEPS_SYSTEM_PROMPT = """
You are a task planning engine for Vunoh Global, a diaspora services company in Kenya.

Given a task intent and its extracted entities, generate a clear, ordered list of fulfilment 
steps that Vunoh's team will follow to complete the task.

Steps must be:
- Specific to the intent (not generic)
- Grounded in real Kenyan operational context
- Between 4 and 6 steps
- Written for an internal operations team, not the customer

Return ONLY a JSON array. No markdown. No explanation. No ```json fences.

Format:
[
  {"step_number": 1, "title": "Short title", "description": "Detailed action description"},
  ...
]
"""

MESSAGES_SYSTEM_PROMPT = """
You are a communications specialist for Vunoh Global, a diaspora services company helping 
Kenyans abroad manage tasks back home.

Given a task summary and a task code, produce confirmation messages for three channels.

CHANNEL RULES:
- whatsapp: Conversational, warm, uses natural line breaks, 1-2 relevant emojis only. 
  2-4 short paragraphs. Address the customer directly.
- email: Formal, structured, professional. Include a subject line on the first line as 
  "Subject: <subject here>". Full details. Sign off as "Vunoh Global Support Team".
- sms: MAXIMUM 145 characters (the task code will be added separately). 
  Key action + status only. No emojis.

Return ONLY a JSON object. No markdown. No explanation. No ```json fences.

Format:
{
  "whatsapp": "<full WhatsApp message>",
  "email": "<full email including Subject: line>",
  "sms": "<SMS body, max 145 chars>"
}
"""


def _call_gemini(system_prompt: str, user_content: str) -> str:
    """
    Make a call to the Gemini API and return the raw text response.
    Raises an exception if the API key is missing or the call fails.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt,
            generation_config={
                'temperature': 0.2,   # Low temp = more consistent, structured output
                'max_output_tokens': 1500,
            }
        )

        response = model.generate_content(user_content)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise


def _safe_parse_json(raw: str) -> Union[dict, list]:
    """
    Safely parse JSON from the model's response.
    Strips markdown code fences if the model added them despite instructions.
    """
    # Remove markdown code fences if present
    cleaned = re.sub(r'```(?:json)?\s*', '', raw).strip()
    cleaned = cleaned.rstrip('`').strip()
    return json.loads(cleaned)


def extract_intent_and_entities(customer_message: str) -> dict:
    """
    Step 1 of the pipeline: extract intent and entities from the customer's message.
    Returns a dict matching the EXTRACTION_SYSTEM_PROMPT schema.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — using fallback mock extraction")
        return _mock_extraction(customer_message)

    try:
        raw = _call_gemini(EXTRACTION_SYSTEM_PROMPT, customer_message)
        result = _safe_parse_json(raw)
        logger.info(f"AI extraction succeeded: intent={result.get('intent')}")
        return result
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Extraction failed: {e} | Raw response: {raw if 'raw' in dir() else 'N/A'}")
        return _mock_extraction(customer_message)


def generate_steps(intent: str, entities: dict, summary: str) -> list:
    """
    Step 2: generate ordered fulfilment steps for the task.
    Returns a list of step dicts.
    """
    if not settings.GEMINI_API_KEY:
        return _mock_steps(intent)

    user_content = f"""
Intent: {intent}
Summary: {summary}
Entities: {json.dumps(entities, indent=2)}

Generate the fulfilment steps for this task.
"""
    try:
        raw = _call_gemini(STEPS_SYSTEM_PROMPT, user_content)
        steps = _safe_parse_json(raw)
        if not isinstance(steps, list):
            raise ValueError("Steps response is not a list")
        logger.info(f"AI generated {len(steps)} steps for intent={intent}")
        return steps
    except Exception as e:
        logger.error(f"Step generation failed: {e}")
        return _mock_steps(intent)


def generate_messages(task_code: str, intent: str, summary: str, entities: dict) -> dict:
    """
    Step 3: generate WhatsApp, Email, and SMS messages for the task.
    Returns dict with keys: whatsapp, email, sms.
    """
    if not settings.GEMINI_API_KEY:
        return _mock_messages(task_code, summary)

    user_content = f"""
Task Code: {task_code}
Intent: {intent}
Summary: {summary}
Key Details: {json.dumps(entities, indent=2)}

Generate the three confirmation messages.
"""
    try:
        raw = _call_gemini(MESSAGES_SYSTEM_PROMPT, user_content)
        messages = _safe_parse_json(raw)
        # Ensure SMS is within limit
        if len(messages.get('sms', '')) > 145:
            messages['sms'] = messages['sms'][:142] + '...'
        logger.info(f"AI generated messages for task {task_code}")
        return messages
    except Exception as e:
        logger.error(f"Message generation failed: {e}")
        return _mock_messages(task_code, summary)


# ─────────────────────────────────────────────
# MOCK FALLBACKS — used when API key is missing
# or for testing without burning API quota
# ─────────────────────────────────────────────

def _mock_extraction(message: str) -> dict:
    """Returns a plausible mock extraction for testing."""
    message_lower = message.lower()
    
    if any(w in message_lower for w in ['send', 'transfer', 'money', 'kes', 'ksh', 'mpesa']):
        intent = 'send_money'
    elif any(w in message_lower for w in ['clean', 'lawyer', 'errand', 'hire', 'service', 'fundi']):
        intent = 'hire_service'
    elif any(w in message_lower for w in ['verify', 'document', 'title', 'deed', 'certificate', 'id']):
        intent = 'verify_document'
    elif any(w in message_lower for w in ['airport', 'pickup', 'transfer', 'jkia', 'arrive']):
        intent = 'get_airport_transfer'
    elif any(w in message_lower for w in ['status', 'update', 'check', 'vnh-']):
        intent = 'check_status'
    else:
        intent = 'hire_service'

    urgency = any(w in message_lower for w in ['urgent', 'asap', 'today', 'immediately', 'emergency', 'now', 'tonight'])

    return {
        'intent': intent,
        'confidence': 0.85,
        'entities': {
            'amount': 15000 if 'send_money' == intent else None,
            'recipient_name': 'Jane Wanjiku' if 'send_money' == intent else None,
            'recipient_phone': None,
            'recipient_relationship': 'mother' if 'send_money' == intent else None,
            'location': 'Nairobi',
            'service_type': 'cleaning' if 'hire_service' == intent else None,
            'document_type': 'land title' if 'verify_document' == intent else None,
            'urgency': urgency,
            'urgency_reason': 'Customer specified urgent' if urgency else None,
            'scheduled_date': None,
            'additional_notes': f'Mock extraction of: {message[:80]}'
        },
        'summary': f'Customer request: {message[:120]}'
    }


def _mock_steps(intent: str) -> list:
    """Returns mock steps based on intent."""
    steps_map = {
        'send_money': [
            {'step_number': 1, 'title': 'Verify Sender Identity', 'description': 'Confirm sender KYC documents and account standing.'},
            {'step_number': 2, 'title': 'Confirm Recipient Details', 'description': 'Verify recipient name, phone number, and bank/M-Pesa details.'},
            {'step_number': 3, 'title': 'Risk Review', 'description': 'Finance team reviews transaction against AML and fraud rules.'},
            {'step_number': 4, 'title': 'Initiate Transfer', 'description': 'Process payment via M-Pesa or bank transfer channel.'},
            {'step_number': 5, 'title': 'Send Confirmation', 'description': 'Notify both sender and recipient via SMS and WhatsApp.'},
        ],
        'hire_service': [
            {'step_number': 1, 'title': 'Capture Service Requirements', 'description': 'Record full service details: type, location, date, budget.'},
            {'step_number': 2, 'title': 'Match Service Provider', 'description': 'Search verified provider network for the requested service and area.'},
            {'step_number': 3, 'title': 'Provider Confirmation', 'description': 'Contact selected provider and confirm availability and pricing.'},
            {'step_number': 4, 'title': 'Schedule & Brief', 'description': 'Schedule service and brief provider with customer requirements.'},
            {'step_number': 5, 'title': 'Completion Sign-off', 'description': 'Collect completion confirmation and customer satisfaction feedback.'},
        ],
        'verify_document': [
            {'step_number': 1, 'title': 'Receive Document Copies', 'description': 'Collect scanned copies of documents from the customer.'},
            {'step_number': 2, 'title': 'Legal Team Assignment', 'description': 'Assign to a qualified legal officer with relevant expertise.'},
            {'step_number': 3, 'title': 'Registry Search', 'description': 'Conduct official search at relevant government registry (e.g., Lands Registry).'},
            {'step_number': 4, 'title': 'Verification Report', 'description': 'Prepare a written verification report with findings and risks.'},
            {'step_number': 5, 'title': 'Deliver Results', 'description': 'Share report with customer via email and secure portal.'},
        ],
        'get_airport_transfer': [
            {'step_number': 1, 'title': 'Confirm Flight Details', 'description': 'Verify flight number, arrival airport, and time.'},
            {'step_number': 2, 'title': 'Assign Driver', 'description': 'Match a vetted driver to the pickup location and time.'},
            {'step_number': 3, 'title': 'Share Driver Details', 'description': 'Send driver name, car, and contact to customer.'},
            {'step_number': 4, 'title': 'Day-of Confirmation', 'description': 'Driver confirms readiness 2 hours before pickup.'},
        ],
        'check_status': [
            {'step_number': 1, 'title': 'Locate Task', 'description': 'Search database using provided task code or customer details.'},
            {'step_number': 2, 'title': 'Compile Status Update', 'description': 'Gather latest status from relevant team.'},
            {'step_number': 3, 'title': 'Respond to Customer', 'description': 'Send updated status via the customer\'s preferred channel.'},
        ],
    }
    return steps_map.get(intent, steps_map['hire_service'])


def _mock_messages(task_code: str, summary: str) -> dict:
    """Returns mock messages for testing."""
    return {
        'whatsapp': (
            f"Hi there! 👋 We've received your request and we're on it.\n\n"
            f"*Request:* {summary[:100]}\n"
            f"*Your Task Code:* {task_code}\n\n"
            f"Our team will review this shortly and keep you updated. "
            f"You can use your task code to check status at any time. 🇰🇪"
        ),
        'email': (
            f"Subject: Your Vunoh Task Confirmation — {task_code}\n\n"
            f"Dear Valued Customer,\n\n"
            f"Thank you for using Vunoh Global. We have received your request and a task has been created.\n\n"
            f"Task Reference: {task_code}\n"
            f"Request Summary: {summary[:200]}\n\n"
            f"Our team will review your request and contact you within 24 hours with a full update.\n\n"
            f"You may check your task status at any time using your task code on our platform.\n\n"
            f"Warm regards,\n"
            f"Vunoh Global Support Team"
        ),
        'sms': f"Vunoh task received. Ref: {task_code}. We'll update you shortly."
    }
