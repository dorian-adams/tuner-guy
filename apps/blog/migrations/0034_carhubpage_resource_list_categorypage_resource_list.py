# Generated by Django 4.2.4 on 2023-08-30 23:37

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0033_alter_blogpage_featured_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='carhubpage',
            name='resource_list',
            field=wagtail.fields.StreamField([('resources', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(max_length=40)), ('urls', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('url', wagtail.blocks.URLBlock()), ('anchor', wagtail.blocks.CharBlock(max_length=40)), ('type', wagtail.blocks.ChoiceBlock(choices=[('TunerGuy', 'TunerGuy'), ('YouTube', 'YouTube'), ('Forums', 'Foruns'), ('Social', 'Social Media'), ('Article', 'Article'), ('Magazine', 'Magazine')]))])))]))], blank=True, null=True, use_json_field=True),
        ),
        migrations.AddField(
            model_name='categorypage',
            name='resource_list',
            field=wagtail.fields.StreamField([('resources', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(max_length=40)), ('urls', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('url', wagtail.blocks.URLBlock()), ('anchor', wagtail.blocks.CharBlock(max_length=40)), ('type', wagtail.blocks.ChoiceBlock(choices=[('TunerGuy', 'TunerGuy'), ('YouTube', 'YouTube'), ('Forums', 'Foruns'), ('Social', 'Social Media'), ('Article', 'Article'), ('Magazine', 'Magazine')]))])))]))], blank=True, null=True, use_json_field=True),
        ),
    ]
