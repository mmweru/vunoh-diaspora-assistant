from rest_framework import serializers
from .models import Task, TaskStep, TaskMessage, StatusHistory


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = ['id', 'step_number', 'title', 'description', 'is_complete']


class TaskMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMessage
        fields = ['id', 'channel', 'subject', 'body', 'created_at']


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_at', 'note']


class TaskSerializer(serializers.ModelSerializer):
    steps = TaskStepSerializer(many=True, read_only=True)
    messages = TaskMessageSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_code', 'original_request', 'intent', 'entities',
            'risk_score', 'risk_level', 'risk_reasons', 'assigned_team',
            'status', 'created_at', 'updated_at',
            'steps', 'messages', 'status_history'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Lighter serializer for the dashboard list view (no nested steps/messages)."""
    class Meta:
        model = Task
        fields = [
            'id', 'task_code', 'original_request', 'intent', 'entities',
            'risk_score', 'risk_level', 'assigned_team', 'status',
            'created_at', 'updated_at'
        ]


class CreateTaskSerializer(serializers.Serializer):
    """Validates the incoming customer request."""
    message = serializers.CharField(
        min_length=5,
        max_length=2000,
        error_messages={
            'min_length': 'Your request is too short. Please describe what you need.',
            'max_length': 'Your request is too long. Please keep it under 2000 characters.',
            'blank': 'Please enter your request.',
        }
    )


class UpdateStatusSerializer(serializers.Serializer):
    """Validates a status update request."""
    status = serializers.ChoiceField(choices=['pending', 'in_progress', 'completed', 'cancelled'])
    note = serializers.CharField(max_length=300, required=False, allow_blank=True)
