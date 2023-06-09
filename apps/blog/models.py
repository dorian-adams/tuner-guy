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


# -----------------------------------------------------------------------------
# Abstract Models
# -----------------------------------------------------------------------------


class BaseCategory(Page):
    """
    Represents a base category page within the application.

    Attributes:
        intro (RichTextField): The introductory text for the category page.
        youtube_embeds (StreamField): A stream field for adding YouTube embeds.

    Usage:
        ``BaseCategory`` serves as a base class for creating category pages.
    """

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

    class Meta:
        abstract = True


# -----------------------------------------------------------------------------
# Concrete Models
# -----------------------------------------------------------------------------


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


class CarHubPage(BaseCategory):
    """
    Represents a type of Category Page for a specific car.

    Hierarchy example: www.TunerGuy.com/Fiesta-ST/

    Attributes:
        reddit_embeds (ForeignKey): A foreign key relationship to a RedditEmbed instance
            representing the Reddit embeds associated with the ``CarHubPage``.

    Usage:
        Create a content hub for a specific car. Store all categories, posts, reddit/youtube
        embeds related to the car.

        Note:
        - The parent page must be a BlogIndexPage.
        - The subpage must be a CategoryPage.
    """

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


class CategoryPage(BaseCategory):
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
    """
    Represents a comment on a ``BlogPage``.

    Attributes:
        page (ParentalKey): The blog page associated with the comment.
        text (TextField): The content of the comment.
        user (ForeignKey): The user who posted the comment.
        created_at (DateTimeField): The date and time when the comment was created.
        updated_at (DateTimeField): The date and time when the comment was last updated.
        is_approved (BooleanField): Indicates whether the comment is approved or not.
            Comments are not displayed on the Blog Page until approved.
    """

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
    """
    Represents a Reddit embed snippet used on ``CategoryPage`` and ``CarHubPage``.

    Uses function, ``get_reddit_posts``, to get and store the embed code
    for two reddit posts.

    Attributes:
        title (CharField): The title or name of the embed.
        subreddit (CharField): The subreddit associated with the embed.
            As "mysubreddit". Not "/r/mysubreddit". This should be provided without
            the "/r/" prefix, only the subreddit name.
        _embed_codes (TextField): Stores the embed codes as a delimited string.

    Properties:
        - embed_codes (list): Returns the embed codes as a list.

    Methods:
        - save(*args, **kwargs): Overrides the default save method to fetch and store
          the top Reddit posts for the specified subreddit upon creation.
    """

    title = models.CharField(max_length=20)
    subreddit = models.CharField(
        max_length=15, validators=[validate_subreddit_format, validate_subreddit_exists]
    )
    _embed_codes = models.TextField(blank=True, null=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("subreddit"),
    ]

    @property
    def embed_codes(self):
        """Return embed codes as a list."""
        return self._embed_codes.split("|")

    @embed_codes.setter
    def embed_codes(self, values):
        """Join embed codes to store as a TextField."""
        self._embed_codes = "|".join(values)

    def save(self, *args, **kwargs):
        """If creation - get the top reddit posts for the ``subreddit``."""
        if not self.pk:
            self.embed_codes = get_reddit_posts(self.subreddit)
        return super().save(*args, **kwargs)
