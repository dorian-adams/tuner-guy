# Generated by Django 4.2.1 on 2023-06-30 21:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0031_remove_categorypage_has_latest_post_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categorypage",
            name="date_of_last_post",
            field=models.DateField(blank=True, null=True),
        ),
    ]