"""
AI Service — Vunoh Global. Uses Groq free API (llama-3.1-8b-instant).
Get free key at: https://console.groq.com
"""

import json, re, logging, requests
from django.conf import settings

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are a structured data extraction engine for Vunoh Global, helping Kenyans abroad manage tasks back home in Kenya.

Analyse the customer message and return ONLY a valid JSON object. No markdown, no explanation, no code fences.

KENYA CONTEXT: Cities: Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, Thika, Nyeri, Kitale. Money: M-Pesa, bank transfer, KES. Documents: title deed, Huduma Namba, KRA PIN, ID, logbook. Services: cleaner, lawyer/wakili, fundi/mechanic, caretaker, driver, nurse.

INTENTS: send_money, hire_service, verify_document, get_airport_transfer, check_status

RETURN EXACTLY:
{"intent":"<intent>","confidence":<0.0-1.0>,"entities":{"amount":<KES number or null>,"recipient_name":"<string or null>","recipient_phone":"<string or null>","recipient_relationship":"<string or null>","location":"<Kenya city/area or null>","service_type":"<string or null>","document_type":"<string or null>","urgency":<true/false>,"urgency_reason":"<string or null>","scheduled_date":"<string or null>","additional_notes":"<string or null>"},"summary":"<one sentence>"}

urgency=true if: urgent, ASAP, today, immediately, emergency, now, tonight. Return ONLY the JSON."""

STEPS_SYSTEM_PROMPT = """Task planning engine for Vunoh Global Kenya diaspora platform. Generate 4-6 specific fulfilment steps.
Return ONLY valid JSON. Format: {"steps":[{"step_number":1,"title":"Short title","description":"Detailed action"},...]}"  No other text."""

MESSAGES_SYSTEM_PROMPT = """Communications specialist for Vunoh Global Kenya diaspora platform.
Generate 3 channel messages. whatsapp: warm, 2-3 paragraphs, 1-2 emojis. email: formal with Subject: line, sign off as Vunoh Global Support Team. sms: MAX 145 chars.
Return ONLY: {"whatsapp":"<msg>","email":"Subject: <subj>\\n\\n<body>","sms":"<max 145 chars>"}"""



def _call_groq(system_prompt, user_content, max_tokens=1000):
    api_key = getattr(settings, 'GROQ_API_KEY', None)
    
    if not api_key or api_key == '':
        logger.error("GROQ_API_KEY not configured in settings")
        raise Exception("GROQ_API_KEY not set. Please add GROQ_API_KEY to your Django settings.")
    
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ], "temperature": 0.1, "max_tokens": max_tokens},
        timeout=30
    )


def _parse(raw):
    cleaned = re.sub(r'```(?:json)?\s*', '', raw).strip().rstrip('`').strip()
    m = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', cleaned)
    return json.loads(m.group(1) if m else cleaned)


def extract_intent_and_entities(message):
    if not getattr(settings, 'GROQ_API_KEY', ''):
        logger.warning("No GROQ_API_KEY — using smart mock")
        return _mock_extraction(message)
    try:
        result = _parse(_call_groq(EXTRACTION_SYSTEM_PROMPT, message))
        logger.info(f"Groq extracted: intent={result.get('intent')}")
        return result
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return _mock_extraction(message)


def generate_steps(intent, entities, summary):
    if not getattr(settings, 'GROQ_API_KEY', ''):
        return _mock_steps(intent)
    try:
        raw = _call_groq(STEPS_SYSTEM_PROMPT, f"Intent: {intent}\nSummary: {summary}\nEntities: {json.dumps(entities)}")
        data = _parse(raw)
        steps = data.get('steps', data) if isinstance(data, dict) else data
        if not isinstance(steps, list): raise ValueError("not a list")
        return steps
    except Exception as e:
        logger.error(f"Steps failed: {e}")
        return _mock_steps(intent)


def generate_messages(task_code, intent, summary, entities):
    if not getattr(settings, 'GROQ_API_KEY', ''):
        return _mock_messages(task_code, summary, intent, entities)
    
    parts = []
    if entities.get('amount'): parts.append(f"KES {entities['amount']:,}")
    if entities.get('recipient_name'): parts.append(f"Recipient: {entities['recipient_name']}")
    if entities.get('location'): parts.append(f"Location: {entities['location']}")
    if entities.get('urgency'): parts.append("URGENT")
    
    try:
        msgs = _parse(_call_groq(MESSAGES_SYSTEM_PROMPT, f"Task: {task_code}\nIntent: {intent}\nSummary: {summary}\nDetails: {', '.join(parts)}"))
        if not isinstance(msgs, dict): raise ValueError("not a dict")
        msgs.setdefault('whatsapp', f"Task {task_code} received. 🇰🇪")
        msgs.setdefault('email', f"Subject: Task {task_code}\n\nReceived. Vunoh Global Support Team")
        msgs.setdefault('sms', f"Vunoh: Task {task_code} received.")
        if len(msgs['sms']) > 145: msgs['sms'] = msgs['sms'][:142] + '...'
        return msgs
    except Exception as e:
        logger.error(f"Messages failed: {e}")
        return _mock_messages(task_code, summary, intent, entities)


def _mock_extraction(message):
    msg = message.lower()
    if any(w in msg for w in ['send','transfer','mpesa','m-pesa','money','kes','ksh','funds']): intent='send_money'
    elif any(w in msg for w in ['verify','document','title','deed','certificate','logbook']): intent='verify_document'
    elif any(w in msg for w in ['airport','jkia','pickup','flight','arrive','land']): intent='get_airport_transfer'
    elif any(w in msg for w in ['status','check','update','vnh-']): intent='check_status'
    else: intent='hire_service'

    urgency = any(w in msg for w in ['urgent','asap','immediately','emergency','now','today','tonight'])
    
    amount = None
    for pat in [r'kes\s*([\d,]+)', r'ksh\s*([\d,]+)', r'([\d,]+)\s*kes', r'([\d,]+)\s*ksh']:
        m = re.search(pat, msg)
        if m:
            try: amount = int(m.group(1).replace(',','')); break
            except: pass
    
    pm = re.search(r'(07\d{8}|01\d{8}|\+2547\d{8})', message)
    phone = pm.group(0) if pm else None
    
    recipient_name, recipient_rel = None, None
    rels = ['mother','mum','mama','dad','father','baba','sister','brother','wife','husband','friend','uncle','aunt','cousin','landlord']
    for rel in rels:
        m = re.search(rf'(?:my\s+)?{rel}\s+([A-Z][a-z]+ ?[A-Za-z]*)', message)
        if m:
            recipient_rel = rel
            recipient_name = m.group(1).strip()
            break
    if not recipient_name:
        m = re.search(r'\bto\s+([A-Z][a-z]+ [A-Z][a-z]+)\b', message)
        if m: recipient_name = m.group(1)
    
    location = None
    for loc in ['nairobi','mombasa','kisumu','nakuru','eldoret','thika','kitale','nyeri','westlands','karen','kilimani','ruiru','kiambu','parklands','upperhill','kasarani','embakasi']:
        if loc in msg: location = loc.title(); break

    doc_type = None
    if intent == 'verify_document':
        if any(w in msg for w in ['land','title','deed','plot']): doc_type='land title deed'
        elif 'logbook' in msg: doc_type='vehicle logbook'
        elif 'id' in msg: doc_type='national ID'
        else: doc_type='document'
    
    service_type = None
    if intent == 'hire_service':
        if any(w in msg for w in ['clean','cleaner']): service_type='cleaning'
        elif any(w in msg for w in ['lawyer','wakili','legal']): service_type='legal services'
        elif any(w in msg for w in ['fundi','mechanic']): service_type='mechanical repair'
        elif 'driver' in msg: service_type='driver'
        elif any(w in msg for w in ['nurse','carer']): service_type='healthcare'
        else: service_type='general service'

    return {
        'intent': intent, 'confidence': 0.82,
        'entities': {
            'amount': amount, 'recipient_name': recipient_name, 'recipient_phone': phone,
            'recipient_relationship': recipient_rel, 'location': location,
            'service_type': service_type, 'document_type': doc_type,
            'urgency': urgency, 'urgency_reason': 'Customer specified urgency' if urgency else None,
            'scheduled_date': None, 'additional_notes': None
        },
        'summary': message[:150]
    }


def _mock_steps(intent):
    return {
        'send_money': [
            {'step_number':1,'title':'Verify Sender Identity','description':'Confirm sender KYC documents and account standing.'},
            {'step_number':2,'title':'Confirm Recipient Details','description':'Verify recipient name and M-Pesa/bank account.'},
            {'step_number':3,'title':'AML Risk Review','description':'Finance team runs AML and fraud screening.'},
            {'step_number':4,'title':'Process Transfer','description':'Initiate M-Pesa or bank transfer.'},
            {'step_number':5,'title':'Send Confirmation','description':'Notify both parties via WhatsApp and SMS.'},
        ],
        'hire_service': [
            {'step_number':1,'title':'Capture Requirements','description':'Record service type, location, date, and instructions.'},
            {'step_number':2,'title':'Match Provider','description':'Search verified network for available provider.'},
            {'step_number':3,'title':'Confirm Booking','description':'Contact provider, confirm pricing and schedule.'},
            {'step_number':4,'title':'Brief & Schedule','description':'Brief provider with all customer requirements.'},
            {'step_number':5,'title':'Completion Sign-off','description':'Collect completion confirmation from both parties.'},
        ],
        'verify_document': [
            {'step_number':1,'title':'Receive Document Copies','description':'Customer uploads scanned document copies.'},
            {'step_number':2,'title':'Assign Legal Officer','description':'Assign to qualified legal officer.'},
            {'step_number':3,'title':'Registry Search','description':'Official search at government registry.'},
            {'step_number':4,'title':'Verification Report','description':'Prepare written report with findings.'},
            {'step_number':5,'title':'Deliver Results','description':'Share report via email and secure portal.'},
        ],
        'get_airport_transfer': [
            {'step_number':1,'title':'Confirm Flight Details','description':'Verify flight number, terminal, and arrival time.'},
            {'step_number':2,'title':'Assign Driver','description':'Match vetted driver for pickup.'},
            {'step_number':3,'title':'Share Driver Details','description':'Send customer driver name, car, and phone.'},
            {'step_number':4,'title':'Day-of Confirmation','description':'Driver confirms readiness 2 hours before landing.'},
        ],
        'check_status': [
            {'step_number':1,'title':'Locate Task','description':'Find task using code or customer details.'},
            {'step_number':2,'title':'Compile Update','description':'Gather latest status from relevant team.'},
            {'step_number':3,'title':'Respond','description':'Send status update to customer.'},
        ],
    }.get(intent, [{'step_number':1,'title':'Review Request','description':'Team reviews and processes the request.'}])


def _mock_messages(task_code, summary, intent='', entities=None):
    entities = entities or {}
    emoji = {'send_money':'💸','hire_service':'🛠️','verify_document':'📄','get_airport_transfer':'✈️','check_status':'🔍'}.get(intent,'📋')
    urgency = entities.get('urgency', False)
    urgent_note = "\n\n⚡ *Marked URGENT* — we're prioritising this." if urgency else ""
    
    email_body = f"Subject: Task Confirmation — {task_code}\n\nDear Customer,\n\nThank you for using Vunoh Global. Your request has been received.\n\nTask Reference: {task_code}\nSummary: {summary}"
    if urgency:
        email_body += "\n\nThis is flagged URGENT and will be prioritised."
    email_body += "\n\nWe will contact you within 24 hours.\n\nWarm regards,\nVunoh Global Support Team"
    
    return {
        'whatsapp': f"{emoji} Hi! We've received your request.\n\n*Summary:* {summary}\n*Task Code:* `{task_code}`{urgent_note}\n\nOur team is on it. Reply with your task code anytime to check status. 🇰🇪",
        'email': email_body,
        'sms': f"Vunoh: Task received. Ref: {task_code}. We'll update you shortly."
    }
