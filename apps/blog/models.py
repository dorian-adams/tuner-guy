from datetime import date

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Max
from django.core.validators import MinLengthValidator

from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from apps.base.blocks import FeaturedContentBlock, YoutubeEmbedBlock


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

    subpage_types = ["CarHubPage", "CategoryPage"]


class CarHubPage(Page):
    intro = RichTextField()
    youtube_embeds = StreamField(
        [
            (
                "Youtube",
                YoutubeEmbedBlock(),
            )
        ],
        use_json_field=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("youtube_embeds"),
    ]

    parent_page_types = ["BlogIndexPage"]
    subpage_types = ["CategoryPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        categories = CategoryPage.objects.descendant_of(self).prefetch_related(
            "category_posts"
        )

        category_with_latest_post = categories.filter(has_latest_post=True).first()

        latest_post = (
            category_with_latest_post.category_posts.first()
            if category_with_latest_post
            else None
        )

        context["posts_per_category"] = [
            {
                "category": category,
                "posts": category.category_posts.exclude(
                    pk=latest_post.pk
                ).select_related("featured_image", "author")[:3],
            }
            for category in categories
        ]
        context["latest_post"] = latest_post

        return context


class CategoryPage(Page):
    intro = RichTextField()
    has_latest_post = models.BooleanField(default=False)

    parent_page_types = ["BlogIndexPage", "CarHubPage"]
    subpage_types = ["BlogPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        return context


class BlogPage(Page):
    category = ParentalKey(
        CategoryPage,
        on_delete=models.CASCADE,
        related_name="category_posts",
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    date = models.DateField(default=date.today)
    snippet = models.CharField(
        max_length=200,
        help_text="Excerpt used in the article's preview card.",
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
    )
    tags = ClusterTaggableManager(through="BlogPageTag", blank=True)
    body = RichTextField()

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("date"),
                FieldPanel("tags"),
            ],
            heading="Blog Information",
        ),
        FieldPanel("snippet"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
    ]

    parent_page_types = ["CategoryPage"]
    subpage_types = []

    def save(self, clean=True, user=None, log_action=False, **kwargs):
        parent_category = self.get_parent().specific
        self.category = parent_category

        latest_category = (
            CategoryPage.objects.sibling_of(parent_category)
            .filter(has_latest_post=True)
            .first()
        )

        if parent_category.pk != getattr(latest_category, "pk", None):
            parent_category.has_latest_post = True
            parent_category.save()
            if latest_category is not None:
                latest_category.has_latest_post = False
                latest_category.save()

        return super().save(clean, user, log_action, **kwargs)


class BlogPageTag(TaggedItemBase):
    """
    Attaches tagging to ``BlogPage``.
    """

    content_object = ParentalKey(
        "blog.BlogPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogComment(models.Model):
    page = ParentalKey(
        "BlogPage", on_delete=models.CASCADE, related_name="page_comments"
    )
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters.")]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comment_author",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    panels = [
        FieldPanel("page"),
        FieldPanel("text"),
        FieldPanel("user"),
        FieldPanel("is_approved"),
    ]
