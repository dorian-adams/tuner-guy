# Generated by Django 4.2.1 on 2023-06-08 01:48

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0008_remove_blogindexpage_featured_cars_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogindexpage",
            name="featured_car",
        ),
        migrations.AddField(
            model_name="blogindexpage",
            name="featured_cars",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Car",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(max_length=20),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.CharBlock(max_length=50),
                                ),
                                ("url", wagtail.blocks.URLBlock()),
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(),
                                ),
                            ]
                        ),
                    )
                ],
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.DeleteModel(
            name="FeaturedCar",
        ),
    ]