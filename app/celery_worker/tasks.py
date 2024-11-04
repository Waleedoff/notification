from app.celery_worker.app import init_app, stop_http_errors
from app.config import config

celery = init_app(config=config)


@celery.task()
def test_task(*args, **kwargs) -> str:
    return "test task is ok"


@celery.task(bind=True)
@stop_http_errors
def send_notification_task(*args, **kwargs) -> str:
    from app.celery_worker.send_notification_task import send_notification_task_
    # if you need to revoke this task make sure to pass task_id=entity.id in args
    # send_notification_task.AsyncResult(task_id).revoke()
    return send_notification_task_(*args, **kwargs)
