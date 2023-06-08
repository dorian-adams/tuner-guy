from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class FeaturedContentBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=20)
    description = blocks.CharBlock(max_length=80)
    url = blocks.URLBlock()
    image = ImageChooserBlock()

    class Meta:
        template = "blocks/featured_content_block.html"
