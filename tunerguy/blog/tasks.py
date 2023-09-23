from config.celery import app
from tunerguy.blog.models import RedditEmbed


@app.task
def update_reddit():
    embeds = RedditEmbed.objects.all()

    for reddit_embed in embeds:
        reddit_embed.update_embedded_posts()
        reddit_embed.save()
