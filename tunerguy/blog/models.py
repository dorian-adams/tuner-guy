from datetime import date

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Prefetch
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from tunerguy.base.blocks import (
    ContentStreamBlock,
    FeaturedContentBlock,
    ResourceStreamBlock,
    YoutubeEmbedBlock,
)
from tunerguy.base.reddit_api import get_reddit_posts

from .validators import validate_subreddit_exists, validate_subreddit_format

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
    resource_list = StreamField(
        ResourceStreamBlock(),
        use_json_field=True,
        blank=True,
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
        FieldPanel("resource_list"),
    ]

    parent_page_types = ["BlogIndexPage"]
    subpage_types = ["CategoryPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        blog_page_query = (
            BlogPage.objects.select_related(
                "author",
            )
            .live()
            .only(
                "snippet",
                "title",
                "date",
                "featured_image",
                "author__first_name",
                "author__last_name",
                "url_path",
                "page_ptr_id",
                "category_id",
            )
            .order_by("-date")[:3]
        )

        categories = (
            CategoryPage.objects.descendant_of(self)
            .live()
            .order_by("-date_of_last_post")
            .only("title", "url_path")
            .prefetch_related(
                Prefetch(
                    "category_posts",
                    queryset=blog_page_query,
                    to_attr="posts",
                )
            )
        )

        context["categories"] = categories
        context["reddit_embeds"] = (
            self.reddit_embeds.embed_codes if self.reddit_embeds else []
        )

        return context


class CategoryPage(BaseCategory):
    date_of_last_post = models.DateField(null=True, blank=True)

    parent_page_types = ["BlogIndexPage", "CarHubPage"]
    subpage_types = ["BlogPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        posts = (
            BlogPage.objects.descendant_of(self)
            .select_related(
                "author",
            )
            .live()
            .order_by("-date")
            .only(
                "snippet",
                "title",
                "date",
                "featured_image",
                "author__first_name",
                "author__last_name",
                "url_path",
                "page_ptr_id",
                "category_id",
            )
        )

        context["latest_post"] = posts[0]
        context["posts"] = posts[1::]

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
    featured_image = models.ImageField(upload_to="featured_image/%Y/%m/%d/")
    tags = ClusterTaggableManager(through="BlogPageTag", blank=True)
    body = StreamField(ContentStreamBlock(), use_json_field=True)

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
        parent_category.date_of_last_post = date.today()
        self.category = parent_category
        parent_category.save()

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
        validators=[
            MinLengthValidator(3, "Comment must be greater than 3 characters.")
        ]
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
        max_length=15,
        validators=[validate_subreddit_format, validate_subreddit_exists],
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

    def update_embedded_posts(self):
        embeds = get_reddit_posts(self.subreddit)
        self._embed_codes = "|".join(embeds)

    def save(self, *args, **kwargs):
        """If creation - get the top reddit posts for the ``subreddit``."""
        if not self.pk:
            self.update_embedded_posts()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.subreddit
