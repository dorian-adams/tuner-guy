import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tunerguy.settings.dev")

app = Celery(
    "tunerguy", broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0")
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()


# Schedule tasks using a later signal since the tasks are outside this module.
# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from tunerguy.apps.blog.tasks import update_reddit

    # Update all RedditEmbed's with the latest posts from their respective subreddit's.
    sender.add_periodic_task(
        timedelta(hours=24),
        update_reddit.s(),
    )
