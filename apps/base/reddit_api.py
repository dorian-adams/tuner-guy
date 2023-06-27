import os
import praw

from prawcore.exceptions import NotFound


def authenticate():
    return praw.Reddit(
        client_id=os.environ.get("REDDIT_ID"),
        client_secret=os.environ.get("REDDIT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USER"),
        password=os.environ.get("REDDIT_USER_PW"),
    )


def get_reddit_posts(subreddit):
    reddit = authenticate()
    subreddit = reddit.subreddit(subreddit)

    moderators = [mod.name for mod in subreddit.moderator()]

    top_posts = []
    for submission in subreddit.hot(limit=10):
        # Exclude posts from moderators to avoid pinned posts,
        # announcements, etc. And, exlude posts that contain the
        # character the list will be joined and split on, "|", to
        # ensure accuracy.
        if submission.author not in moderators and "|" not in submission.title:
            embed_code = create_embed_code(submission)
            top_posts.append(embed_code)
            if len(top_posts) == 2:
                break

    return top_posts


def create_embed_code(submission):
    return (
        f'<blockquote class="reddit-card" style="height:316px" data-embed-height="316">'
        f'<a href="https://www.reddit.com{submission.permalink}">{submission.title}</a><br> by'
        f'<a href="https://www.reddit.com/user/{submission.author}">u/{submission.author}</a> in '
        f'<a href="https://www.reddit.com{submission.subreddit.url}">{submission.subreddit}</a></blockquote>'
    )


def subreddit_found(subreddit):
    """
    See: https://github.com/reddit-archive/reddit/blob/master/r2/r2/controllers/api.py#L4587
    """
    reddit = authenticate()
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
        return True
    except NotFound:
        return False
