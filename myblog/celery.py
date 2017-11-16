# # from __future__ import absolute_import, unicode_literals
# # from celery import Celery

# # app = Celery('myblog',
# #              broker='amqp://',
# #              backend='amqp://',
# #              include=['myblog.tasks'])

# # # Optional configuration, see the application user guide.
# # app.conf.update(
# #     result_expires=3600,
# # )

# # if __name__ == '__main__':
# #     app.start()



# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myblog.settings')

# app = Celery('myblog')

# # Using a string here means the worker don't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()


# # @app.task(bind=True)
# # def debug_task(self):
# #     print('Request: {0!r}'.format(self.request))


from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myblog.settings')

from django.conf import settings

app = Celery('myblog')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print ('Request:{0!r}'.format(self.request))


from celery.decorators import periodic_task
from datetime import timedelta
# from blog.models import PostLike
# from blog.views import test

@periodic_task(run_every=timedelta(seconds=30))
def every_30_seconds():
    # test()
    # PostLike.objects.create(ip='000000000')
    print("Running periodic task!")