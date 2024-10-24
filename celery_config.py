from celery import Celery

app = Celery('3d-reconstruction', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    worker_prefetch_multiplier=1,
)
