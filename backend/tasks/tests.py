"""
Test suite for Vunoh Diaspora Assistant.

Run with: python manage.py test tasks
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from .models import Task, TaskStep, TaskMessage, StatusHistory
from .risk_service import calculate_risk
from .assignment_service import assign_team
from .ai_service import _mock_extraction, _mock_steps, _mock_messages


# ─────────────────────────────────────────────
# RISK SERVICE TESTS
# ─────────────────────────────────────────────

class RiskScoringTests(TestCase):

    def test_urgent_large_transfer_is_high_risk(self):
        """Urgent + large amount should produce high risk score."""
        result = calculate_risk('send_money', {
            'urgency': True,
            'amount': 80000,
            'recipient_name': None,
            'recipient_phone': None,
        })
        self.assertGreaterEqual(result['score'], 70)
        self.assertEqual(result['level'], 'high')

    def test_land_title_is_high_risk(self):
        """Land title verification should be high risk."""
        result = calculate_risk('verify_document', {
            'urgency': False,
            'document_type': 'land title deed',
        })
        self.assertGreaterEqual(result['score'], 30)
        self.assertIn('land', result['reasons'][0].lower())

    def test_small_non_urgent_transfer_is_low_risk(self):
        """Small, non-urgent transfer with known recipient should be low risk."""
        result = calculate_risk('send_money', {
            'urgency': False,
            'amount': 2000,
            'recipient_name': 'Jane Wanjiku',
            'recipient_phone': '+254712345678',
        })
        self.assertLess(result['score'], 40)
        self.assertEqual(result['level'], 'low')

    def test_status_check_has_zero_risk(self):
        """Status check should never carry risk."""
        result = calculate_risk('check_status', {})
        self.assertEqual(result['score'], 0)

    def test_score_capped_at_100(self):
        """Risk score should never exceed 100."""
        result = calculate_risk('send_money', {
            'urgency': True,
            'amount': 500000,
            'recipient_name': None,
            'recipient_phone': None,
        })
        self.assertLessEqual(result['score'], 100)

    def test_risk_has_reasons(self):
        """Risk result should always include reasons."""
        result = calculate_risk('hire_service', {'urgency': True, 'service_type': 'cleaner', 'location': 'Nairobi'})
        self.assertIsInstance(result['reasons'], list)
        self.assertGreater(len(result['reasons']), 0)


# ─────────────────────────────────────────────
# ASSIGNMENT SERVICE TESTS
# ─────────────────────────────────────────────

class AssignmentTests(TestCase):

    def test_send_money_goes_to_finance(self):
        self.assertEqual(assign_team('send_money'), 'Finance')

    def test_verify_document_goes_to_legal(self):
        self.assertEqual(assign_team('verify_document'), 'Legal')

    def test_hire_service_goes_to_operations(self):
        self.assertEqual(assign_team('hire_service'), 'Operations')

    def test_airport_transfer_goes_to_operations(self):
        self.assertEqual(assign_team('get_airport_transfer'), 'Operations')

    def test_check_status_goes_to_support(self):
        self.assertEqual(assign_team('check_status'), 'Support')

    def test_unknown_goes_to_support(self):
        self.assertEqual(assign_team('completely_unknown_intent'), 'Support')


# ─────────────────────────────────────────────
# AI SERVICE MOCK TESTS
# ─────────────────────────────────────────────

class AIMockTests(TestCase):

    def test_mock_extraction_detects_send_money(self):
        result = _mock_extraction("I need to send KES 15,000 to my mother in Kisumu")
        self.assertEqual(result['intent'], 'send_money')
        self.assertIn('entities', result)

    def test_mock_extraction_detects_verify_document(self):
        result = _mock_extraction("Please verify my land title deed for the plot in Karen")
        self.assertEqual(result['intent'], 'verify_document')

    def test_mock_extraction_detects_urgency(self):
        result = _mock_extraction("URGENT: send money to my brother immediately")
        self.assertTrue(result['entities']['urgency'])

    def test_mock_steps_returns_list(self):
        steps = _mock_steps('send_money')
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        self.assertIn('title', steps[0])
        self.assertIn('description', steps[0])

    def test_mock_messages_all_channels_present(self):
        messages = _mock_messages('VNH-TEST1', 'Test summary')
        self.assertIn('whatsapp', messages)
        self.assertIn('email', messages)
        self.assertIn('sms', messages)

    def test_mock_sms_includes_task_code(self):
        messages = _mock_messages('VNH-TEST1', 'Test summary')
        self.assertIn('VNH-TEST1', messages['sms'])


# ─────────────────────────────────────────────
# MODEL TESTS
# ─────────────────────────────────────────────

class TaskModelTests(TestCase):

    def test_task_code_is_generated(self):
        task = Task.objects.create(
            original_request='Test request',
            intent='send_money',
            entities={},
            risk_score=20,
            assigned_team='Finance',
        )
        self.assertTrue(task.task_code.startswith('VNH-'))
        self.assertEqual(len(task.task_code), 9)  # VNH- (4) + 5 chars

    def test_risk_level_set_from_score(self):
        task = Task.objects.create(
            original_request='Test',
            intent='send_money',
            entities={},
            risk_score=75,
            assigned_team='Finance',
        )
        self.assertEqual(task.risk_level, 'high')

    def test_medium_risk_level(self):
        task = Task.objects.create(
            original_request='Test',
            intent='hire_service',
            entities={},
            risk_score=50,
            assigned_team='Operations',
        )
        self.assertEqual(task.risk_level, 'medium')


# ─────────────────────────────────────────────
# API ENDPOINT TESTS
# ─────────────────────────────────────────────

class TaskAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Create a sample task directly for GET tests
        self.task = Task.objects.create(
            original_request='I need to send KES 5,000 to my sister in Nairobi',
            intent='send_money',
            entities={'amount': 5000, 'recipient_name': 'Mary', 'urgency': False},
            risk_score=15,
            assigned_team='Finance',
        )
        TaskStep.objects.create(task=self.task, step_number=1, title='Verify Sender', description='Check KYC')
        TaskMessage.objects.create(task=self.task, channel='whatsapp', body='Hi! Your task is received.')
        TaskMessage.objects.create(task=self.task, channel='email', subject='Task Confirmation', body='Dear customer...')
        TaskMessage.objects.create(task=self.task, channel='sms', body=f'Task received. [{self.task.task_code}]')

    def test_get_all_tasks(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', response.data)
        self.assertEqual(response.data['count'], 1)

    def test_get_task_by_code(self):
        response = self.client.get(f'/api/tasks/{self.task.task_code}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['task_code'], self.task.task_code)

    def test_get_task_not_found(self):
        response = self.client.get('/api/tasks/VNH-XXXXX/')
        self.assertEqual(response.status_code, 404)

    def test_update_status(self):
        response = self.client.patch(
            f'/api/tasks/{self.task.task_code}/status/',
            {'status': 'in_progress'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')

    def test_update_invalid_status(self):
        response = self.client.patch(
            f'/api/tasks/{self.task.task_code}/status/',
            {'status': 'flying_to_the_moon'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_status_history_recorded(self):
        self.client.patch(
            f'/api/tasks/{self.task.task_code}/status/',
            {'status': 'in_progress', 'note': 'Started by ops team'},
            format='json'
        )
        history = StatusHistory.objects.filter(task=self.task, new_status='in_progress')
        self.assertTrue(history.exists())
        self.assertEqual(history.first().note, 'Started by ops team')

    def test_create_task_missing_message(self):
        response = self.client.post('/api/tasks/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_task_message_too_short(self):
        response = self.client.post('/api/tasks/', {'message': 'hi'}, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('tasks.views.extract_intent_and_entities')
    @patch('tasks.views.generate_steps')
    @patch('tasks.views.generate_messages')
    def test_create_task_full_flow(self, mock_messages, mock_steps, mock_extract):
        """Test the full task creation pipeline with mocked AI calls."""
        mock_extract.return_value = {
            'intent': 'send_money',
            'entities': {'amount': 10000, 'urgency': False, 'recipient_name': 'Test User', 'recipient_phone': None},
            'summary': 'Send KES 10,000 to Test User'
        }
        mock_steps.return_value = [
            {'step_number': 1, 'title': 'Step 1', 'description': 'Do this'},
        ]
        mock_messages.return_value = {
            'whatsapp': 'WhatsApp message here',
            'email': 'Subject: Test Email\n\nEmail body here',
            'sms': 'Task received. Act now.'
        }

        response = self.client.post(
            '/api/tasks/',
            {'message': 'I need to send KES 10,000 to my friend Test User in Nairobi'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('task_code', response.data)
        self.assertTrue(response.data['task_code'].startswith('VNH-'))
        self.assertEqual(response.data['intent'], 'send_money')
        self.assertEqual(len(response.data['steps']), 1)
        self.assertEqual(len(response.data['messages']), 3)

    def test_get_stats(self):
        response = self.client.get('/api/tasks/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
