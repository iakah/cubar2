from celery import Celery
from nerf_processing import celery

if __name__ == "__main__":
    celery.worker_main()
