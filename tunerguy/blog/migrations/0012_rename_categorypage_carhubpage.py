# Generated by Django 4.2.1 on 2023-06-08 19:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0083_workflowcontenttype"),
        ("blog", "0011_categorypage_intro_categorypage_youtube_embeds"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CategoryPage",
            new_name="CarHubPage",
        ),
    ]