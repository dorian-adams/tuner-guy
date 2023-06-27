# Generated by Django 4.2.1 on 2023-06-23 20:39

from django.db import migrations
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_alter_blogpage_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='carhubpage',
            name='reddit_posts',
            field=wagtail.fields.StreamField([('Subreddit', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(max_length=20)), ('subreddit', wagtail.blocks.CharBlock(max_length=10)), ('top_posts', wagtail.blocks.ListBlock(wagtail.embeds.blocks.EmbedBlock, editable=False))]))], null=True, use_json_field=True),
        ),
    ]
