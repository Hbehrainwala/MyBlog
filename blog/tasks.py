from celery import Celery
from celery.decorators import task
from celery import shared_task


app = Celery('app.celery', broker='amqp://guest:guest@localhost:5672//')

@shared_task
def upload_excel_file(data):
    """ call to upload excel """
    pass