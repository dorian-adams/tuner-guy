from django.core.exceptions import ValidationError

from apps.base.reddit_api import subreddit_found


def validate_subreddit_format(subreddit):
    if not subreddit.isalnum():
        raise ValidationError("Subreddit name cannnot contain any special characters.")


def validate_subreddit_exists(subreddit):
    if not subreddit_found(subreddit):
        raise ValidationError(
            "Subreddit was not found, please check the name or try again later."
        )
