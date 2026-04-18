"""
API Views for Vunoh Diaspora Assistant.

Endpoints:
  POST /api/tasks/          — create a new task from a customer message
  GET  /api/tasks/          — list all tasks (dashboard)
  GET  /api/tasks/<code>/   — retrieve a single task with full details
  PATCH /api/tasks/<code>/status/ — update task status
  GET  /api/tasks/stats/    — dashboard summary statistics
"""

import logging
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Task, TaskStep, TaskMessage, StatusHistory
from .serializers import (
    TaskSerializer, TaskListSerializer,
    CreateTaskSerializer, UpdateStatusSerializer
)
from .ai_service import extract_intent_and_entities, generate_steps, generate_messages
from .risk_service import calculate_risk
from .assignment_service import assign_team

logger = logging.getLogger(__name__)


class TaskListCreateView(APIView):
    """
    GET  /api/tasks/  — list all tasks
    POST /api/tasks/  — create a new task from a customer message
    """

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskListSerializer(tasks, many=True)
        return Response({
            'count': tasks.count(),
            'tasks': serializer.data
        })

    def post(self, request):
        # 1. Validate input
        input_serializer = CreateTaskSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                {'error': 'Invalid input', 'details': input_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer_message = input_serializer.validated_data['message']
        logger.info(f"New task request received: {customer_message[:80]}...")

        try:
            # 2. AI: Extract intent and entities
            ai_result = extract_intent_and_entities(customer_message)
            intent = ai_result.get('intent', 'unknown')
            entities = ai_result.get('entities', {})
            summary = ai_result.get('summary', customer_message[:200])

            # 3. Calculate risk score
            risk_result = calculate_risk(intent, entities)

            # 4. Assign team
            team = assign_team(intent)

            # 5. Create the task in the database
            task = Task.objects.create(
                original_request=customer_message,
                intent=intent,
                entities=entities,
                risk_score=risk_result['score'],
                risk_level=risk_result['level'],
                risk_reasons=risk_result['reasons'],
                assigned_team=team,
                status='pending',
            )

            # Initial status history entry
            StatusHistory.objects.create(
                task=task,
                old_status='',
                new_status='pending',
                note='Task created'
            )

            # 6. AI: Generate fulfilment steps
            steps_data = generate_steps(intent, entities, summary)
            for step in steps_data:
                TaskStep.objects.create(
                    task=task,
                    step_number=step.get('step_number', 1),
                    title=step.get('title', 'Step'),
                    description=step.get('description', ''),
                )

            # 7. AI: Generate three-format messages
            messages_data = generate_messages(task.task_code, intent, summary, entities)

            # Save WhatsApp message
            TaskMessage.objects.create(
                task=task,
                channel='whatsapp',
                body=messages_data.get('whatsapp', '')
            )

            # Save Email message (extract subject from body if present)
            email_body = messages_data.get('email', '')
            email_subject = ''
            if email_body.startswith('Subject:'):
                lines = email_body.split('\n', 2)
                email_subject = lines[0].replace('Subject:', '').strip()
                email_body = '\n'.join(lines[1:]).strip()

            TaskMessage.objects.create(
                task=task,
                channel='email',
                subject=email_subject,
                body=email_body
            )

            # Save SMS message — append task code
            sms_body = messages_data.get('sms', '')
            full_sms = f"{sms_body} [{task.task_code}]"
            TaskMessage.objects.create(
                task=task,
                channel='sms',
                body=full_sms
            )

            # 8. Return the full task to the frontend
            task.refresh_from_db()
            serializer = TaskSerializer(task)
            logger.info(f"Task {task.task_code} created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(f"Error creating task: {e}")
            return Response(
                {'error': 'We could not process your request right now. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(APIView):
    """
    GET /api/tasks/<task_code>/ — retrieve full task details
    """

    def get(self, request, task_code):
        try:
            task = Task.objects.get(task_code=task_code.upper())
        except Task.DoesNotExist:
            return Response(
                {'error': f'No task found with code {task_code.upper()}'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TaskSerializer(task)
        return Response(serializer.data)


class TaskStatusUpdateView(APIView):
    """
    PATCH /api/tasks/<task_code>/status/ — update task status
    """

    def patch(self, request, task_code):
        try:
            task = Task.objects.get(task_code=task_code.upper())
        except Task.DoesNotExist:
            return Response(
                {'error': f'No task found with code {task_code.upper()}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid status', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = serializer.validated_data['status']
        note = serializer.validated_data.get('note', '')

        if new_status == task.status:
            return Response(
                {'message': f'Task is already {new_status}'},
                status=status.HTTP_200_OK
            )

        # Record history before changing
        StatusHistory.objects.create(
            task=task,
            old_status=task.status,
            new_status=new_status,
            note=note
        )

        task.status = new_status
        task.save()

        logger.info(f"Task {task.task_code} status updated to {new_status}")
        return Response({
            'task_code': task.task_code,
            'status': task.status,
            'message': f'Status updated to {new_status}'
        })


class DashboardStatsView(APIView):
    """
    GET /api/tasks/stats/ — summary stats for the dashboard header
    """

    def get(self, request):
        total = Task.objects.count()
        by_status = dict(
            Task.objects.values('status').annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        by_intent = dict(
            Task.objects.values('intent').annotate(count=Count('id'))
            .values_list('intent', 'count')
        )
        high_risk = Task.objects.filter(risk_level='high').count()

        return Response({
            'total': total,
            'by_status': {
                'pending': by_status.get('pending', 0),
                'in_progress': by_status.get('in_progress', 0),
                'completed': by_status.get('completed', 0),
                'cancelled': by_status.get('cancelled', 0),
            },
            'by_intent': by_intent,
            'high_risk_count': high_risk,
        })
