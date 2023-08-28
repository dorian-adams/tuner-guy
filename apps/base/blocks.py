from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class FeaturedContentBlock(blocks.StructBlock):
    """
    Represents a block for displaying featured content.
    """

    title = blocks.CharBlock(max_length=20)
    description = blocks.CharBlock(max_length=80)
    url = blocks.URLBlock()
    image = ImageChooserBlock()

    class Meta:
        template = "blocks/featured_content_block.html"


class YoutubeEmbedBlock(blocks.StructBlock):
    """
    Represents a block for embedding YouTube videos (block of 4).

    Attributes:
        youtube_link (EmbedBlock): The embedded YouTube video link.
        source_name (CharBlock): The name of the YouTube channel.
        source_url (URLBlock): The URL to the YouTube channel for citation purposes.
    """

    youtube_link = EmbedBlock(max_width=520, max_height=350)
    source_name = blocks.CharBlock()
    source_url = blocks.URLBlock()

    class Meta:
        max_num = min_num = 4
        template = "blocks/youtube_embed_block.html"
