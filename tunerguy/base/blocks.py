from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from .validators import validate_youtube_channel, validate_youtube_embed


class FeaturedContentBlock(blocks.StructBlock):
    """
    Represents a block for displaying featured content.
    """

    title = blocks.CharBlock(max_length=20)
    description = blocks.CharBlock(max_length=80)
    url = blocks.URLBlock(label="Page URL")
    image = ImageChooserBlock()

    class Meta:
        template = "blocks/featured_content_block.html"


class YoutubeEmbedBlock(blocks.StructBlock):
    """
    Represents a block for embedding YouTube videos (block of 4).

    Attributes:
        video (URLBlock): The YouTube video embed link. Must contain '/embed/'.
        channel_name (CharBlock): The name of the YouTube channel.
        channel_url (URLBlock): The URL to the YouTube channel for citation purposes.
    """

    video = blocks.URLBlock(
        validators=[validate_youtube_embed],
        help_text="Must be a YouTube embed URL.",
    )
    channel_name = blocks.CharBlock()
    channel_url = blocks.URLBlock(
        validators=[validate_youtube_channel],
        help_text="e.g. https://www.youtube.com/@ChannelName",
        label="Channel URL",
    )

    class Meta:
        icon = "media"
        template = "blocks/youtube_embed_block.html"


class ResourceURLBlock(blocks.StructBlock):
    url = blocks.URLBlock(help_text="External or internal URL.")
    anchor = blocks.CharBlock(label="Anchor text", max_length=40)
    type = blocks.ChoiceBlock(
        choices=[
            ("TunerGuy", "TunerGuy"),
            ("YouTube", "YouTube"),
            ("Forums", "Foruns"),
            ("Social", "Social Media"),
            ("Article", "Article"),
            ("Magazine", "Magazine"),
        ],
    )


class ResourceCategoryBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=40)
    urls = blocks.ListBlock(ResourceURLBlock())


class ResourceStreamBlock(blocks.StreamBlock):
    resources = ResourceCategoryBlock(icon="clipboard-list")

    class Meta:
        template = "blocks/resource_stream_block.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(max_length=100, required=False)

    class Meta:
        icon = "image"
        template = "blocks/image_block.html"


class HeadingBlock(blocks.StructBlock):
    heading_text = blocks.CharBlock(classname="title")
    size = blocks.ChoiceBlock(
        choices=[
            ("", "Select a Header size"),
            ("h2", "H2"),
            ("h3", "H3"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"


class QuoteBlock(blocks.StructBlock):
    quote_text = blocks.TextBlock()
    attribute_name = blocks.CharBlock(blank=True, required=False)

    class Meta:
        icon = "openquote"
        template = "blocks/quote_block.html"


class ContentStreamBlock(blocks.StreamBlock):
    heading_block = HeadingBlock()
    paragraph_block = blocks.RichTextBlock(
        template="blocks/paragraph_block.html"
    )
    image_block = ImageBlock()
    quote_block = QuoteBlock(required=False)
    youtube_embed_block = YoutubeEmbedBlock(required=False)
