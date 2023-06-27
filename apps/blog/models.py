from datetime import date

from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator

from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from .validators import validate_subreddit_exists, validate_subreddit_format
from apps.base.blocks import FeaturedContentBlock, YoutubeEmbedBlock
from apps.base.reddit_api import get_reddit_posts


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
    reddit_embeds = models.ForeignKey(
        "blog.RedditEmbed",
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("youtube_embeds"),
        FieldPanel("reddit_embeds"),
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
        context["reddit_embeds"] = (
            self.reddit_embeds.embed_codes if self.reddit_embeds else []
        )

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
    category = models.ForeignKey(
        CategoryPage,
        blank=True,
        null=True,
        related_name="category_posts",
        on_delete=models.CASCADE,
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


@register_snippet
class BlogComment(models.Model):
    page = ParentalKey(
        "BlogPage",
        related_name="page_comments",
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters.")]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comment_author",
        on_delete=models.PROTECT,
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


@register_snippet
class RedditEmbed(models.Model):
    title = models.CharField(max_length=20)
    subreddit = models.CharField(
        max_length=15, validators=[validate_subreddit_format, validate_subreddit_exists]
    )
    last_updated = models.DateField(blank=True, null=True)
    _embed_codes = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("subreddit"),
    ]

    @property
    def embed_codes(self):
        return self._embed_codes.split("|")

    @embed_codes.setter
    def embed_codes(self, values):
        self._embed_codes = "|".join(values)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.embed_codes = get_reddit_posts(self.subreddit)
        return super().save(*args, **kwargs)
