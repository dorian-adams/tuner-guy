from django.db import models

from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

from apps.base.blocks import FeaturedContentBlock


class BlogIndexPage(Page):
    """
    Homepage.

    """

    template = "blog/home_page.html"
    featured_cars = StreamField(
        [
            (
                "Car",
                FeaturedContentBlock(),
            ),
        ],
        use_json_field=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("featured_cars"),
    ]


class CategoryPage(Page):
    pass


class BlogPage(Page):
    pass
