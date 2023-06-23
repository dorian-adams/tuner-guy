# Generated by Django 4.2.1 on 2023-06-08 04:52

from django.db import migrations
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_alter_blogindexpage_featured_cars'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorypage',
            name='intro',
            field=wagtail.fields.RichTextField(default='Temp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='categorypage',
            name='youtube_embeds',
            field=wagtail.fields.StreamField([('Youtube', wagtail.blocks.StructBlock([('youtube_link', wagtail.embeds.blocks.EmbedBlock(max_height=350, max_width=520)), ('source_name', wagtail.blocks.CharBlock()), ('source_url', wagtail.blocks.URLBlock())]))], null=True, use_json_field=True),
        ),
    ]
