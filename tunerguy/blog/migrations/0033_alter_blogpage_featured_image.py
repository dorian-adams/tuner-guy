# Generated by Django 4.2.4 on 2023-08-28 20:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0032_alter_categorypage_date_of_last_post"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="featured_image",
            field=models.ImageField(upload_to="featured_image/%Y/%m/%d/"),
        ),
    ]
