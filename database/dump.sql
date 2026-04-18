-- ═══════════════════════════════════════════════════════════
-- Vunoh Diaspora Assistant — SQL Dump
-- Schema + 5 sample tasks with complete data
-- Generated: 2026-04-16
-- ═══════════════════════════════════════════════════════════

DROP TABLE IF EXISTS tasks_statushistory;
DROP TABLE IF EXISTS tasks_taskmessage;
DROP TABLE IF EXISTS tasks_taskstep;
DROP TABLE IF EXISTS tasks_task;

CREATE TABLE "tasks_statushistory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "old_status" varchar(20) NOT NULL, "new_status" varchar(20) NOT NULL, "changed_at" datetime NOT NULL, "note" varchar(300) NOT NULL, "task_id" char(32) NOT NULL REFERENCES "tasks_task" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "tasks_task" ("id" char(32) NOT NULL PRIMARY KEY, "task_code" varchar(20) NOT NULL UNIQUE, "original_request" text NOT NULL, "intent" varchar(50) NOT NULL, "entities" text NOT NULL CHECK ((JSON_VALID("entities") OR "entities" IS NULL)), "risk_score" integer NOT NULL, "risk_level" varchar(10) NOT NULL, "risk_reasons" text NOT NULL CHECK ((JSON_VALID("risk_reasons") OR "risk_reasons" IS NULL)), "assigned_team" varchar(50) NOT NULL, "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);

CREATE TABLE "tasks_taskmessage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "channel" varchar(20) NOT NULL, "subject" varchar(300) NOT NULL, "body" text NOT NULL, "created_at" datetime NOT NULL, "task_id" char(32) NOT NULL REFERENCES "tasks_task" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "tasks_taskstep" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "step_number" integer unsigned NOT NULL CHECK ("step_number" >= 0), "title" varchar(200) NOT NULL, "description" text NOT NULL, "is_complete" bool NOT NULL, "task_id" char(32) NOT NULL REFERENCES "tasks_task" ("id") DEFERRABLE INITIALLY DEFERRED);


-- tasks_task
INSERT INTO tasks_task (id, task_code, original_request, intent, entities, risk_score, risk_level, risk_reasons, assigned_team, status, created_at, updated_at) VALUES ('8318d882ae7d484ba6fd2440d8a75139', 'VNH-D7TL2', 'I need to send KES 25,000 to my mother in Kisumu urgently. Her name is Grace Akinyi and her M-Pesa is 0712345678.', 'send_money', '{"amount": 25000, "recipient_name": "Grace Akinyi", "recipient_phone": "0712345678", "recipient_relationship": "mother", "location": "Kisumu", "urgency": true, "urgency_reason": "Customer specified urgent", "service_type": null, "document_type": null, "scheduled_date": null, "additional_notes": "M-Pesa transfer to mother in Kisumu"}', 55, 'medium', '["Urgency flag: customer marked request as urgent (+20).", "Moderate transfer amount: KES 25,000 (+10).", "No recipient phone number verified in system (+10)."]', 'Finance', 'in_progress', '2026-04-16 16:23:34.651773', '2026-04-16 16:23:34.651820');
INSERT INTO tasks_task (id, task_code, original_request, intent, entities, risk_score, risk_level, risk_reasons, assigned_team, status, created_at, updated_at) VALUES ('a6572b0864f7477c89a15b287fc65967', 'VNH-LLWGO', 'Please verify my land title deed for the plot I own in Karen, Nairobi. I want to make sure it''s genuine before I finalize a sale.', 'verify_document', '{"amount": null, "recipient_name": null, "recipient_phone": null, "recipient_relationship": null, "location": "Karen, Nairobi", "urgency": false, "urgency_reason": null, "service_type": null, "document_type": "land title deed", "scheduled_date": null, "additional_notes": "Customer wants to verify before finalizing a property sale"}', 30, 'low', '["Land title verification (+30). Land fraud is among the most prevalent financial crimes in Kenya."]', 'Legal', 'pending', '2026-04-16 16:23:34.765732', '2026-04-16 16:23:34.765773');
INSERT INTO tasks_task (id, task_code, original_request, intent, entities, risk_score, risk_level, risk_reasons, assigned_team, status, created_at, updated_at) VALUES ('8df2c6758089418c9224052d4e33a42d', 'VNH-C4RI3', 'Can someone clean my apartment in Westlands this Friday? It''s a 3-bedroom flat and I need a thorough deep clean before my family visits.', 'hire_service', '{"amount": null, "recipient_name": null, "recipient_phone": null, "recipient_relationship": null, "location": "Westlands, Nairobi", "urgency": false, "urgency_reason": null, "service_type": "deep cleaning", "document_type": null, "scheduled_date": "This Friday", "additional_notes": "3-bedroom flat, deep clean required before family visit"}', 5, 'low', '["Service hire in Westlands: within verified provider network (+5)."]', 'Operations', 'completed', '2026-04-16 16:23:34.864559', '2026-04-16 16:23:34.864584');
INSERT INTO tasks_task (id, task_code, original_request, intent, entities, risk_score, risk_level, risk_reasons, assigned_team, status, created_at, updated_at) VALUES ('601f4d56ab21401cbc29018146ae480c', 'VNH-US19M', 'I''m arriving at JKIA on Thursday at 6pm on Kenya Airways KQ101. I need a driver to pick me up and take me to Westlands.', 'get_airport_transfer', '{"amount": null, "recipient_name": null, "recipient_phone": null, "recipient_relationship": null, "location": "JKIA to Westlands, Nairobi", "urgency": false, "urgency_reason": null, "service_type": "airport pickup", "document_type": null, "scheduled_date": "Thursday 6:00 PM", "additional_notes": "Flight KQ101, Kenya Airways, JKIA Terminal 1A"}', 5, 'low', '["Airport transfer: standard low risk (+5)."]', 'Operations', 'pending', '2026-04-16 16:23:34.981207', '2026-04-16 16:23:34.981228');
INSERT INTO tasks_task (id, task_code, original_request, intent, entities, risk_score, risk_level, risk_reasons, assigned_team, status, created_at, updated_at) VALUES ('72a703b87303439c9cedb61c9edbbbe7', 'VNH-9SQTO', 'URGENT — I need KES 150,000 sent to someone called John right now. No time to waste. Bank transfer.', 'send_money', '{"amount": 150000, "recipient_name": "John", "recipient_phone": null, "recipient_relationship": null, "location": null, "urgency": true, "urgency_reason": "Customer marked URGENT, no time to waste", "service_type": null, "document_type": null, "scheduled_date": null, "additional_notes": "High risk: large urgent transfer to partially identified recipient"}', 100, 'high', '["Urgency flag: customer marked request as urgent (+20). Urgency is a common trigger in diaspora wire fraud.", "Very large transfer amount: KES 150,000 (+30). Transfers above KES 100k require enhanced due diligence.", "Unknown recipient: only first name provided, no phone number (+25).", "Urgency + large amount combination (+15 bonus). Most common wire fraud pattern.", "Score capped at 100."]', 'Finance', 'pending', '2026-04-16 16:23:35.066319', '2026-04-16 16:23:35.066341');

-- tasks_taskstep
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (1, 1, 'Verify Sender Identity', 'Confirm sender KYC documents and account standing in Vunoh system.', 0, '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (2, 2, 'Confirm Recipient Details', 'Verify Grace Akinyi''s M-Pesa number 0712345678 is active and matches name.', 0, '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (3, 3, 'Risk Review', 'Finance team reviews KES 25,000 urgent transfer against AML rules.', 0, '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (4, 4, 'Initiate Transfer', 'Process M-Pesa transfer to 0712345678 in Kisumu.', 0, '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (5, 5, 'Send Confirmation', 'Notify sender via WhatsApp and recipient via SMS upon completion.', 0, '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (6, 1, 'Receive Document Copies', 'Collect scanned copies of the land title deed from the customer via secure portal.', 0, 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (7, 2, 'Legal Team Assignment', 'Assign to a qualified legal officer with property law expertise.', 0, 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (8, 3, 'Lands Registry Search', 'Conduct official search at Nairobi Lands Registry for the Karen plot.', 0, 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (9, 4, 'Verification Report', 'Prepare written verification report with findings, encumbrances, and recommendations.', 0, 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (10, 5, 'Deliver Results', 'Share report with customer via email and secure document portal.', 0, 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (11, 1, 'Capture Service Requirements', 'Record: 3-bedroom deep clean, Westlands, Friday, pre-family visit standard.', 1, '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (12, 2, 'Match Service Provider', 'Search verified cleaning provider network for Westlands area availability on Friday.', 1, '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (13, 3, 'Provider Confirmation', 'Contact selected cleaner, confirm availability, pricing, and time slot.', 1, '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (14, 4, 'Schedule & Brief', 'Confirm Friday booking and brief provider: 3-bed, deep clean, access instructions.', 1, '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (15, 5, 'Completion Sign-off', 'Collect completion photo evidence and customer satisfaction confirmation.', 1, '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (16, 1, 'Confirm Flight Details', 'Verify KQ101 arrival time and terminal at JKIA with Kenya Airways.', 0, '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (17, 2, 'Assign Vetted Driver', 'Match an available, background-checked driver for Thursday 6pm JKIA pickup.', 0, '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (18, 3, 'Share Driver Details', 'Send customer the driver''s name, vehicle, registration, and phone number.', 0, '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (19, 4, 'Day-of Confirmation', 'Driver confirms flight status and readiness 2 hours before landing.', 0, '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (20, 1, '⚠️ HOLD — High Risk Review', 'Task flagged HIGH RISK. Do NOT process until senior Finance officer approves.', 0, '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (21, 2, 'Contact Sender', 'Call customer to verify identity and confirm relationship with ''John''.', 0, '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (22, 3, 'Full Recipient KYC', 'Obtain full recipient name, phone, bank account, and ID before proceeding.', 0, '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (23, 4, 'AML Compliance Check', 'Run full AML check on both sender and recipient for KES 150,000.', 0, '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (24, 5, 'Senior Approval', 'Senior Finance officer must approve before transfer is initiated.', 0, '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskstep (id, step_number, title, description, is_complete, task_id) VALUES (25, 6, 'Process or Decline', 'Proceed with transfer upon approval or decline and notify customer with reason.', 0, '72a703b87303439c9cedb61c9edbbbe7');

-- tasks_taskmessage
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (1, 'whatsapp', '', 'Hi! 👋 We''ve received your urgent transfer request.

*Amount:* KES 25,000
*Recipient:* Grace Akinyi, Kisumu
*M-Pesa:* 0712345678

Our Finance team is reviewing this now. You''ll hear from us within the hour. 🇰🇪', '2026-04-16 16:23:34.715963', '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (2, 'email', 'Urgent Transfer Request Received — VNH-D7TL2', 'Dear Valued Customer,

Thank you for using Vunoh Global. We have received your urgent money transfer request.

Task Reference: VNH-D7TL2
Amount: KES 25,000
Recipient: Grace Akinyi
Location: Kisumu
M-Pesa: 0712345678

Our Finance team will process this within 1 hour. You will receive a confirmation SMS once the transfer is complete.

Warm regards,
Vunoh Global Support Team', '2026-04-16 16:23:34.725880', '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (3, 'sms', '', 'Vunoh: Transfer of KES 25,000 to Grace Akinyi (Kisumu) is being processed. [VNH-D7TL2]', '2026-04-16 16:23:34.735654', '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (4, 'whatsapp', '', 'Hello! 📄 We''ve received your land title verification request for your Karen plot.

Our Legal team will conduct an official Lands Registry search and send you a full verification report.

*Note:* This process takes 2-3 business days. We''ll keep you updated every step of the way.', '2026-04-16 16:23:34.824476', 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (5, 'email', 'Land Title Verification Request — VNH-LLWGO', 'Dear Valued Customer,

Thank you for contacting Vunoh Global. We have received your request to verify the land title deed for your property in Karen, Nairobi.

Task Reference: VNH-LLWGO
Document Type: Land Title Deed
Location: Karen, Nairobi
Purpose: Pre-sale verification

Our Legal team will conduct an official search at the Nairobi Lands Registry and provide you with a comprehensive verification report within 2-3 business days.

Please upload a scanned copy of your title deed via our secure portal to begin the process.

Warm regards,
Vunoh Global Legal Team', '2026-04-16 16:23:34.834306', 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (6, 'sms', '', 'Vunoh: Land title verification for Karen plot received. Legal team will contact you in 2-3 days. [VNH-LLWGO]', '2026-04-16 16:23:34.844477', 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (7, 'whatsapp', '', 'Great news! 🧹 We''ve received your cleaning request for Westlands.

*Service:* 3-bedroom deep clean
*Location:* Westlands, Nairobi
*When:* This Friday

Our Operations team is matching you with a verified cleaner right now. We''ll confirm the booking and share the cleaner''s details within a few hours!', '2026-04-16 16:23:34.924081', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (8, 'email', 'Cleaning Service Request Confirmed — VNH-C4RI3', 'Dear Valued Customer,

Thank you for using Vunoh Global. We have received your cleaning service request.

Task Reference: VNH-C4RI3
Service Type: 3-Bedroom Deep Clean
Location: Westlands, Nairobi
Scheduled Date: This Friday

Our Operations team will match you with a verified, background-checked cleaning professional and confirm all details within 4 hours.

Warm regards,
Vunoh Global Operations Team', '2026-04-16 16:23:34.933263', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (9, 'sms', '', 'Vunoh: Deep clean for Westlands apt (Friday) confirmed. Provider details coming shortly. [VNH-C4RI3]', '2026-04-16 16:23:34.942186', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (10, 'whatsapp', '', '✈️ We''ve got your airport transfer sorted!

*Flight:* KQ101 — Thursday, 6:00 PM
*Pickup:* JKIA → Westlands

We''re assigning you a verified driver now. You''ll receive their name, car details, and phone number at least 3 hours before your flight lands. Safe travels! 🇰🇪', '2026-04-16 16:23:35.025162', '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (11, 'email', 'Airport Transfer Booking Confirmed — VNH-US19M', 'Dear Valued Customer,

Thank you for booking an airport transfer with Vunoh Global.

Task Reference: VNH-US19M
Flight: Kenya Airways KQ101
Arrival: Thursday, 6:00 PM
Pickup: JKIA
Destination: Westlands, Nairobi

We will assign you a vetted driver and share their full details (name, vehicle, registration, and phone) at least 3 hours before your scheduled arrival.

Warm regards,
Vunoh Global Operations Team', '2026-04-16 16:23:35.034723', '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (12, 'sms', '', 'Vunoh: Airport pickup KQ101 (Thu 6PM, JKIA→Westlands) confirmed. Driver details coming. [VNH-US19M]', '2026-04-16 16:23:35.045569', '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (13, 'whatsapp', '', '⚠️ We''ve received your transfer request for KES 150,000.

Due to the amount and urgency, our compliance team needs to do a quick verification before we proceed. A member of our Finance team will call you within 30 minutes.

This is to protect you. Please have your ID ready.', '2026-04-16 16:23:35.132090', '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (14, 'email', 'Important: Verification Required for Your Transfer — VNH-9SQTO', 'Dear Valued Customer,

We have received your request to transfer KES 150,000.

Task Reference: VNH-9SQTO
Amount: KES 150,000
Recipient: John (details incomplete)
Status: PENDING VERIFICATION

Due to the size of this transfer and our commitment to protecting our customers from fraud, our compliance team requires additional verification before we can proceed.

A Finance team member will contact you within 30 minutes. Please have your identification documents ready.

Warm regards,
Vunoh Global Finance & Compliance Team', '2026-04-16 16:23:35.140430', '72a703b87303439c9cedb61c9edbbbe7');
INSERT INTO tasks_taskmessage (id, channel, subject, body, created_at, task_id) VALUES (15, 'sms', '', 'Vunoh: KES 150,000 transfer on hold. Compliance check required. We''ll call you in 30 mins. [VNH-9SQTO]', '2026-04-16 16:23:35.148480', '72a703b87303439c9cedb61c9edbbbe7');

-- tasks_statushistory
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (1, '', 'pending', '2026-04-16 16:23:34.745737', 'Task created', '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (2, 'pending', 'in_progress', '2026-04-16 16:23:34.755125', 'Assigned to team', '8318d882ae7d484ba6fd2440d8a75139');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (3, '', 'pending', '2026-04-16 16:23:34.853400', 'Task created', 'a6572b0864f7477c89a15b287fc65967');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (4, '', 'pending', '2026-04-16 16:23:34.952556', 'Task created', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (5, 'pending', 'in_progress', '2026-04-16 16:23:34.963115', 'Assigned to team', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (6, 'in_progress', 'completed', '2026-04-16 16:23:34.971824', 'Service delivered', '8df2c6758089418c9224052d4e33a42d');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (7, '', 'pending', '2026-04-16 16:23:35.054615', 'Task created', '601f4d56ab21401cbc29018146ae480c');
INSERT INTO tasks_statushistory (id, old_status, new_status, changed_at, note, task_id) VALUES (8, '', 'pending', '2026-04-16 16:23:35.155828', 'Task created', '72a703b87303439c9cedb61c9edbbbe7');