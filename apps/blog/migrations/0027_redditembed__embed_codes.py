# Generated by Django 4.2.1 on 2023-06-25 03:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0026_redditembed_remove_carhubpage_reddit_posts_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="redditembed",
            name="_embed_codes",
            field=models.TextField(blank=True, null=True),
        ),
    ]
