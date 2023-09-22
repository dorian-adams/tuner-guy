# Generated by Django 4.2.1 on 2023-06-24 04:19

import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0023_alter_carhubpage_reddit_posts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="carhubpage",
            name="reddit_posts",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Subreddit",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(max_length=20),
                                ),
                                (
                                    "subreddit",
                                    wagtail.blocks.CharBlock(max_length=10),
                                ),
                                (
                                    "top_posts",
                                    wagtail.blocks.ListBlock(
                                        wagtail.embeds.blocks.EmbedBlock(
                                            required=False
                                        ),
                                        required=False,
                                    ),
                                ),
                                (
                                    "last_updated",
                                    wagtail.blocks.DateBlock(required=False),
                                ),
                            ]
                        ),
                    )
                ],
                null=True,
                use_json_field=True,
            ),
        ),
    ]
