import re

from django.core.exceptions import ValidationError


def validate_youtube_embed(url):
    # Ensure YouTube embed URL is used.
    pattern = r"^https://www\.youtube\.com/embed/"

    if not re.match(pattern, url):
        raise ValidationError(
            "URL must be of the following format: https://www.youtube.com/embed/"
        )


def validate_youtube_channel(url):
    # Ensure YouTube channel URL is used.
    pattern = r"^https://www\.youtube\.com/@"

    if not re.match(pattern, url):
        raise ValidationError(
            "URL must be of the following format: https://www.youtube.com/@ChannelName"
        )
