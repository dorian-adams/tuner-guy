from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class FeaturedContentBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=20)
    description = blocks.CharBlock(max_length=80)
    url = blocks.URLBlock()
    image = ImageChooserBlock()

    class Meta:
        template = "blocks/featured_content_block.html"


class YoutubeEmbedBlock(blocks.StructBlock):
    youtube_link = EmbedBlock(max_width=520, max_height=350)
    source_name = blocks.CharBlock()
    source_url = blocks.URLBlock()

    class Meta:
        template = "blocks/youtube_embed_block.html"
        max_num = 4
        min_num = 4
