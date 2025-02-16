from apscheduler.schedulers.background import BackgroundScheduler
from app.application.events.reservation_event import consume_event
# from app.infrastructure.messaging.rabbitmq import consume_event


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(consume_event, 'interval', minutes=1)
    scheduler.start()
