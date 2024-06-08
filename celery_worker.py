from celery import Celery
from celery.schedules import crontab
from imports import *
from utils import Utility

app = Celery("worker", broker="redis://redis:6379/0", include=['celery_worker'])


app.conf.beat_schedule = {
    'call-save-all-products-every-hour': {
        'task': 'celery_worker.call_periodic_task',
        'schedule': crontab(minute=0, hour='*'),  # Executes at the start of every hour
    },
}

@app.task
def call_periodic_task():
    # Example function that gets called
    print("execution started")
    category_response = requests.post("http://web:3000/list-categories")
    products_response = requests.post("http://web:3000/save-all-products")
    update_vectorstore = Utility.get_vectorstore('1', True)
    update_vectorstore = Utility.get_vectorstore('2', True)
    print("Periodic task executed")
