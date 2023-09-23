# Generated by Django 4.2.1 on 2023-06-07 19:25

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0002_blogpage_categorypage_featuredcar_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogindexpage",
            name="featured_car",
            field=wagtail.fields.StreamField(
                [
                    (
                        "title",
                        wagtail.blocks.CharBlock(form_classname="title"),
                    ),
                    ("url", wagtail.blocks.CharBlock(form_classname="slug")),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                ],
                null=True,
                use_json_field=True,
            ),
        ),
    ]