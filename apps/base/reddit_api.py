"""
reddit_utils module

This module provides utility functions to interact with the Reddit API and retrieve
information about Reddit posts and subreddits.

Module Functions:
    - authenticate(): Authenticates and returns a Reddit instance.
    - get_reddit_posts(subreddit): Retrieves the top Reddit posts from the specified subreddit.
    - create_embed_code(submission): Creates an embed code for a Reddit submission.
    - subreddit_found(subreddit): Checks if a subreddit exists.
"""

import os
import praw

from prawcore.exceptions import NotFound


def authenticate():
    """
    Authenticates and returns a Reddit instance.

    Returns:
        praw.Reddit: Authenticated Reddit instance using the provided credentials.
    """
    return praw.Reddit(
        client_id=os.environ.get("REDDIT_ID"),
        client_secret=os.environ.get("REDDIT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USER"),
        password=os.environ.get("REDDIT_USER_PW"),
    )


def get_reddit_posts(subreddit):
    """
    Retrieves the top Reddit posts from the specified subreddit.

    Args:
        subreddit (str): The name of the subreddit.

    Returns:
        list: A list of embed codes for the top Reddit posts.
    """
    reddit = authenticate()
    subreddit = reddit.subreddit(subreddit)

    moderators = [mod.name for mod in subreddit.moderator()]

    top_posts = []
    for submission in subreddit.hot(limit=10):
        # Exclude posts from moderators to avoid pinned posts,
        # announcements, etc. Exlude posts that contain the
        # character the list will be joined and split on, "|".
        if submission.author not in moderators and "|" not in submission.title:
            embed_code = create_embed_code(submission)
            top_posts.append(embed_code)
            if len(top_posts) == 2:
                break

    return top_posts


def create_embed_code(submission):
    """
    Creates an embed code for a Reddit submission.

    Args:
        submission (praw.models.Submission): The Reddit submission object.

    Returns:
        str: The embed code for the Reddit submission.
    """
    return (
        f'<blockquote class="reddit-card" style="height:316px" data-embed-height="316">'
        f'<a href="https://www.reddit.com{submission.permalink}">{submission.title}</a><br> by'
        f'<a href="https://www.reddit.com/user/{submission.author}">u/{submission.author}</a> in '
        f'<a href="https://www.reddit.com{submission.subreddit.url}">{submission.subreddit}</a></blockquote>'
    )


def subreddit_found(subreddit):
    """
    Checks if a subreddit exists.

    praw raises 404 when a subreddit isn't found.
    See: https://github.com/reddit-archive/reddit/blob/master/r2/r2/controllers/api.py#L4587

    Args:
        subreddit (str): The name of the subreddit.

    Returns:
        bool: True if the subreddit exists, False otherwise.
    """
    reddit = authenticate()
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
        return True
    except NotFound:
        return False
