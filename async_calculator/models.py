from django.db import models
import uuid


class AsyncCalculationTask(models.Model):
    TASK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_id = models.IntegerField()
    task_token = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    input_data = models.JSONField(default=dict)
    result_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'async_calculation_tasks'
        indexes = [
            models.Index(fields=['application_id']),
            models.Index(fields=['task_token']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Task {self.id} - App {self.application_id}"