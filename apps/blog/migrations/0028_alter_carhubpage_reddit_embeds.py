# Generated by Django 4.2.1 on 2023-06-26 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_redditembed__embed_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carhubpage',
            name='reddit_embeds',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='blog.redditembed'),
        ),
    ]
