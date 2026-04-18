"""
Management command to seed the database with 5 sample tasks.
Run with: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from tasks.models import Task, TaskStep, TaskMessage, StatusHistory


SAMPLE_TASKS = [
    {
        "original_request": "I need to send KES 25,000 to my mother in Kisumu urgently. Her name is Grace Akinyi and her M-Pesa is 0712345678.",
        "intent": "send_money",
        "entities": {
            "amount": 25000,
            "recipient_name": "Grace Akinyi",
            "recipient_phone": "0712345678",
            "recipient_relationship": "mother",
            "location": "Kisumu",
            "urgency": True,
            "urgency_reason": "Customer specified urgent",
            "service_type": None,
            "document_type": None,
            "scheduled_date": None,
            "additional_notes": "M-Pesa transfer to mother in Kisumu"
        },
        "risk_score": 55,
        "risk_level": "medium",
        "risk_reasons": [
            "Urgency flag: customer marked request as urgent (+20).",
            "Moderate transfer amount: KES 25,000 (+10).",
            "No recipient phone number verified in system (+10)."
        ],
        "assigned_team": "Finance",
        "status": "in_progress",
        "steps": [
            {"step_number": 1, "title": "Verify Sender Identity", "description": "Confirm sender KYC documents and account standing in Vunoh system."},
            {"step_number": 2, "title": "Confirm Recipient Details", "description": "Verify Grace Akinyi's M-Pesa number 0712345678 is active and matches name."},
            {"step_number": 3, "title": "Risk Review", "description": "Finance team reviews KES 25,000 urgent transfer against AML rules."},
            {"step_number": 4, "title": "Initiate Transfer", "description": "Process M-Pesa transfer to 0712345678 in Kisumu."},
            {"step_number": 5, "title": "Send Confirmation", "description": "Notify sender via WhatsApp and recipient via SMS upon completion."},
        ],
        "messages": {
            "whatsapp": "Hi! 👋 We've received your urgent transfer request.\n\n*Amount:* KES 25,000\n*Recipient:* Grace Akinyi, Kisumu\n*M-Pesa:* 0712345678\n\nOur Finance team is reviewing this now. You'll hear from us within the hour. 🇰🇪",
            "email_subject": "Urgent Transfer Request Received — {task_code}",
            "email": "Dear Valued Customer,\n\nThank you for using Vunoh Global. We have received your urgent money transfer request.\n\nTask Reference: {task_code}\nAmount: KES 25,000\nRecipient: Grace Akinyi\nLocation: Kisumu\nM-Pesa: 0712345678\n\nOur Finance team will process this within 1 hour. You will receive a confirmation SMS once the transfer is complete.\n\nWarm regards,\nVunoh Global Support Team",
            "sms": "Vunoh: Transfer of KES 25,000 to Grace Akinyi (Kisumu) is being processed."
        }
    },
    {
        "original_request": "Please verify my land title deed for the plot I own in Karen, Nairobi. I want to make sure it's genuine before I finalize a sale.",
        "intent": "verify_document",
        "entities": {
            "amount": None,
            "recipient_name": None,
            "recipient_phone": None,
            "recipient_relationship": None,
            "location": "Karen, Nairobi",
            "urgency": False,
            "urgency_reason": None,
            "service_type": None,
            "document_type": "land title deed",
            "scheduled_date": None,
            "additional_notes": "Customer wants to verify before finalizing a property sale"
        },
        "risk_score": 30,
        "risk_level": "medium",
        "risk_reasons": [
            "Land title verification (+30). Land fraud is among the most prevalent financial crimes in Kenya."
        ],
        "assigned_team": "Legal",
        "status": "pending",
        "steps": [
            {"step_number": 1, "title": "Receive Document Copies", "description": "Collect scanned copies of the land title deed from the customer via secure portal."},
            {"step_number": 2, "title": "Legal Team Assignment", "description": "Assign to a qualified legal officer with property law expertise."},
            {"step_number": 3, "title": "Lands Registry Search", "description": "Conduct official search at Nairobi Lands Registry for the Karen plot."},
            {"step_number": 4, "title": "Verification Report", "description": "Prepare written verification report with findings, encumbrances, and recommendations."},
            {"step_number": 5, "title": "Deliver Results", "description": "Share report with customer via email and secure document portal."},
        ],
        "messages": {
            "whatsapp": "Hello! 📄 We've received your land title verification request for your Karen plot.\n\nOur Legal team will conduct an official Lands Registry search and send you a full verification report.\n\n*Note:* This process takes 2-3 business days. We'll keep you updated every step of the way.",
            "email_subject": "Land Title Verification Request — {task_code}",
            "email": "Dear Valued Customer,\n\nThank you for contacting Vunoh Global. We have received your request to verify the land title deed for your property in Karen, Nairobi.\n\nTask Reference: {task_code}\nDocument Type: Land Title Deed\nLocation: Karen, Nairobi\nPurpose: Pre-sale verification\n\nOur Legal team will conduct an official search at the Nairobi Lands Registry and provide you with a comprehensive verification report within 2-3 business days.\n\nPlease upload a scanned copy of your title deed via our secure portal to begin the process.\n\nWarm regards,\nVunoh Global Legal Team",
            "sms": "Vunoh: Land title verification for Karen plot received. Legal team will contact you in 2-3 days."
        }
    },
    {
        "original_request": "Can someone clean my apartment in Westlands this Friday? It's a 3-bedroom flat and I need a thorough deep clean before my family visits.",
        "intent": "hire_service",
        "entities": {
            "amount": None,
            "recipient_name": None,
            "recipient_phone": None,
            "recipient_relationship": None,
            "location": "Westlands, Nairobi",
            "urgency": False,
            "urgency_reason": None,
            "service_type": "deep cleaning",
            "document_type": None,
            "scheduled_date": "This Friday",
            "additional_notes": "3-bedroom flat, deep clean required before family visit"
        },
        "risk_score": 5,
        "risk_level": "low",
        "risk_reasons": [
            "Service hire in Westlands: within verified provider network (+5)."
        ],
        "assigned_team": "Operations",
        "status": "completed",
        "steps": [
            {"step_number": 1, "title": "Capture Service Requirements", "description": "Record: 3-bedroom deep clean, Westlands, Friday, pre-family visit standard."},
            {"step_number": 2, "title": "Match Service Provider", "description": "Search verified cleaning provider network for Westlands area availability on Friday."},
            {"step_number": 3, "title": "Provider Confirmation", "description": "Contact selected cleaner, confirm availability, pricing, and time slot."},
            {"step_number": 4, "title": "Schedule & Brief", "description": "Confirm Friday booking and brief provider: 3-bed, deep clean, access instructions."},
            {"step_number": 5, "title": "Completion Sign-off", "description": "Collect completion photo evidence and customer satisfaction confirmation."},
        ],
        "messages": {
            "whatsapp": "Great news! 🧹 We've received your cleaning request for Westlands.\n\n*Service:* 3-bedroom deep clean\n*Location:* Westlands, Nairobi\n*When:* This Friday\n\nOur Operations team is matching you with a verified cleaner right now. We'll confirm the booking and share the cleaner's details within a few hours!",
            "email_subject": "Cleaning Service Request Confirmed — {task_code}",
            "email": "Dear Valued Customer,\n\nThank you for using Vunoh Global. We have received your cleaning service request.\n\nTask Reference: {task_code}\nService Type: 3-Bedroom Deep Clean\nLocation: Westlands, Nairobi\nScheduled Date: This Friday\n\nOur Operations team will match you with a verified, background-checked cleaning professional and confirm all details within 4 hours.\n\nWarm regards,\nVunoh Global Operations Team",
            "sms": "Vunoh: Deep clean for Westlands apt (Friday) confirmed. Provider details coming shortly."
        }
    },
    {
        "original_request": "I'm arriving at JKIA on Thursday at 6pm on Kenya Airways KQ101. I need a driver to pick me up and take me to Westlands.",
        "intent": "get_airport_transfer",
        "entities": {
            "amount": None,
            "recipient_name": None,
            "recipient_phone": None,
            "recipient_relationship": None,
            "location": "JKIA to Westlands, Nairobi",
            "urgency": False,
            "urgency_reason": None,
            "service_type": "airport pickup",
            "document_type": None,
            "scheduled_date": "Thursday 6:00 PM",
            "additional_notes": "Flight KQ101, Kenya Airways, JKIA Terminal 1A"
        },
        "risk_score": 5,
        "risk_level": "low",
        "risk_reasons": [
            "Airport transfer: standard low risk (+5)."
        ],
        "assigned_team": "Operations",
        "status": "pending",
        "steps": [
            {"step_number": 1, "title": "Confirm Flight Details", "description": "Verify KQ101 arrival time and terminal at JKIA with Kenya Airways."},
            {"step_number": 2, "title": "Assign Vetted Driver", "description": "Match an available, background-checked driver for Thursday 6pm JKIA pickup."},
            {"step_number": 3, "title": "Share Driver Details", "description": "Send customer the driver's name, vehicle, registration, and phone number."},
            {"step_number": 4, "title": "Day-of Confirmation", "description": "Driver confirms flight status and readiness 2 hours before landing."},
        ],
        "messages": {
            "whatsapp": "✈️ We've got your airport transfer sorted!\n\n*Flight:* KQ101 — Thursday, 6:00 PM\n*Pickup:* JKIA → Westlands\n\nWe're assigning you a verified driver now. You'll receive their name, car details, and phone number at least 3 hours before your flight lands. Safe travels! 🇰🇪",
            "email_subject": "Airport Transfer Booking Confirmed — {task_code}",
            "email": "Dear Valued Customer,\n\nThank you for booking an airport transfer with Vunoh Global.\n\nTask Reference: {task_code}\nFlight: Kenya Airways KQ101\nArrival: Thursday, 6:00 PM\nPickup: JKIA\nDestination: Westlands, Nairobi\n\nWe will assign you a vetted driver and share their full details (name, vehicle, registration, and phone) at least 3 hours before your scheduled arrival.\n\nWarm regards,\nVunoh Global Operations Team",
            "sms": "Vunoh: Airport pickup KQ101 (Thu 6PM, JKIA→Westlands) confirmed. Driver details coming."
        }
    },
    {
        "original_request": "URGENT — I need KES 150,000 sent to someone called John right now. No time to waste. Bank transfer.",
        "intent": "send_money",
        "entities": {
            "amount": 150000,
            "recipient_name": "John",
            "recipient_phone": None,
            "recipient_relationship": None,
            "location": None,
            "urgency": True,
            "urgency_reason": "Customer marked URGENT, no time to waste",
            "service_type": None,
            "document_type": None,
            "scheduled_date": None,
            "additional_notes": "High risk: large urgent transfer to partially identified recipient"
        },
        "risk_score": 100,
        "risk_level": "high",
        "risk_reasons": [
            "Urgency flag: customer marked request as urgent (+20). Urgency is a common trigger in diaspora wire fraud.",
            "Very large transfer amount: KES 150,000 (+30). Transfers above KES 100k require enhanced due diligence.",
            "Unknown recipient: only first name provided, no phone number (+25).",
            "Urgency + large amount combination (+15 bonus). Most common wire fraud pattern.",
            "Score capped at 100."
        ],
        "assigned_team": "Finance",
        "status": "pending",
        "steps": [
            {"step_number": 1, "title": "⚠️ HOLD — High Risk Review", "description": "Task flagged HIGH RISK. Do NOT process until senior Finance officer approves."},
            {"step_number": 2, "title": "Contact Sender", "description": "Call customer to verify identity and confirm relationship with 'John'."},
            {"step_number": 3, "title": "Full Recipient KYC", "description": "Obtain full recipient name, phone, bank account, and ID before proceeding."},
            {"step_number": 4, "title": "AML Compliance Check", "description": "Run full AML check on both sender and recipient for KES 150,000."},
            {"step_number": 5, "title": "Senior Approval", "description": "Senior Finance officer must approve before transfer is initiated."},
            {"step_number": 6, "title": "Process or Decline", "description": "Proceed with transfer upon approval or decline and notify customer with reason."},
        ],
        "messages": {
            "whatsapp": "⚠️ We've received your transfer request for KES 150,000.\n\nDue to the amount and urgency, our compliance team needs to do a quick verification before we proceed. A member of our Finance team will call you within 30 minutes.\n\nThis is to protect you. Please have your ID ready.",
            "email_subject": "Important: Verification Required for Your Transfer — {task_code}",
            "email": "Dear Valued Customer,\n\nWe have received your request to transfer KES 150,000.\n\nTask Reference: {task_code}\nAmount: KES 150,000\nRecipient: John (details incomplete)\nStatus: PENDING VERIFICATION\n\nDue to the size of this transfer and our commitment to protecting our customers from fraud, our compliance team requires additional verification before we can proceed.\n\nA Finance team member will contact you within 30 minutes. Please have your identification documents ready.\n\nWarm regards,\nVunoh Global Finance & Compliance Team",
            "sms": "Vunoh: KES 150,000 transfer on hold. Compliance check required. We'll call you in 30 mins."
        }
    },
]


class Command(BaseCommand):
    help = 'Seed the database with 5 sample tasks including full data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding database with sample tasks...')

        created = 0
        for data in SAMPLE_TASKS:
            task = Task.objects.create(
                original_request=data['original_request'],
                intent=data['intent'],
                entities=data['entities'],
                risk_score=data['risk_score'],
                risk_level=data['risk_level'],
                risk_reasons=data['risk_reasons'],
                assigned_team=data['assigned_team'],
                status=data['status'],
            )

            # Create steps
            for step in data['steps']:
                TaskStep.objects.create(
                    task=task,
                    step_number=step['step_number'],
                    title=step['title'],
                    description=step['description'],
                    is_complete=(data['status'] == 'completed'),
                )

            # Create messages
            msgs = data['messages']
            from tasks.models import TaskMessage
            TaskMessage.objects.create(
                task=task, channel='whatsapp', body=msgs['whatsapp']
            )
            TaskMessage.objects.create(
                task=task, channel='email',
                subject=msgs['email_subject'].replace('{task_code}', task.task_code),
                body=msgs['email'].replace('{task_code}', task.task_code)
            )
            TaskMessage.objects.create(
                task=task, channel='sms',
                body=f"{msgs['sms']} [{task.task_code}]"
            )

            # Status history
            StatusHistory.objects.create(
                task=task, old_status='', new_status='pending', note='Task created'
            )
            if data['status'] in ('in_progress', 'completed'):
                StatusHistory.objects.create(
                    task=task, old_status='pending', new_status='in_progress', note='Assigned to team'
                )
            if data['status'] == 'completed':
                StatusHistory.objects.create(
                    task=task, old_status='in_progress', new_status='completed', note='Service delivered'
                )

            created += 1
            self.stdout.write(f'  ✅ Created task {task.task_code} — {task.intent}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Done! {created} sample tasks created.'))
