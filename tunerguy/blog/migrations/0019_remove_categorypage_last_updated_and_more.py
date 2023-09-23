# Generated by Django 4.2.1 on 2023-06-22 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0018_alter_blogpage_category"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="categorypage",
            name="last_updated",
        ),
        migrations.AddField(
            model_name="categorypage",
            name="has_latest_post",
            field=models.BooleanField(default=False),
        ),
    ]