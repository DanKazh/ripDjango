import time
import logging
import requests
import threading
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from .models import AsyncCalculationTask
from .serializers import CalculationRequestSerializer

logger = logging.getLogger(__name__)


def process_calculation_task_sync(task_id):
    print(f"STARTING calculation for task {task_id}")

    try:
        task = AsyncCalculationTask.objects.get(id=task_id)
        print(f"Task data: {task.input_data}")

        # Спим 3 секунды
        print("⏳ Sleeping 3 seconds...")
        time.sleep(3)

        # Расчет
        resources = task.input_data['resources']
        total_cost = 0

        for resource in resources:
            cost = resource['tariff_cost'] * resource['needed_amount'] * resource['ratio']
            total_cost += cost + 2000
            print(f"Resource {resource['resource_id']}: {cost}")

        print(f"TOTAL CALCULATED: {total_cost}")

        # Пытаемся отправить в Go
        callback_url = "http://localhost:8081/api/async/calculationResult"
        result_data = {
            'application_id': task.input_data['application_id'],
            'resources': [],
            'token': task.task_token,
            'total_cost': int(total_cost)
        }

        print(f"Sending to: {callback_url}")
        response = requests.post(callback_url, json=result_data)
        print(f"Response: {response.status_code}")

    except Exception as e:
        print(f"💥 ERROR: {e}")

@api_view(['POST'])
def start_async_calculation(request):
    """
    Запуск асинхронного расчета для заявки
    """
    serializer = CalculationRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    # Проверка токена
    if data['token'] != settings.ASYNC_PROCESSOR_TOKEN:
        return JsonResponse(
            {'error': 'Invalid token'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Создаем задачу
    task = AsyncCalculationTask.objects.create(
        application_id=data['application_id'],
        task_token=data['token'],
        input_data=data
    )

    # Запускаем обработку в отдельном потоке
    thread = threading.Thread(target=process_calculation_task_sync, args=(task.id,))
    thread.daemon = True
    thread.start()

    return JsonResponse({
        'task_id': str(task.id),
        'status': 'processing_started',
        'message': 'Calculation started'
    })


@api_view(['GET'])
def task_status(request, task_id):
    """
    Проверка статуса задачи
    """
    try:
        task = AsyncCalculationTask.objects.get(id=task_id)
        return JsonResponse({
            'task_id': str(task.id),
            'status': task.status,
            'created_at': task.created_at,
            'processed_at': task.processed_at,
            'error_message': task.error_message
        })
    except AsyncCalculationTask.DoesNotExist:
        return JsonResponse(
            {'error': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )