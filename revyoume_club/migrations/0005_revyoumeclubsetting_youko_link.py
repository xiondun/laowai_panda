# Generated by Django 2.1.7 on 2020-02-19 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revyoume_club', '0004_auto_20200212_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='revyoumeclubsetting',
            name='youko_link',
            field=models.URLField(default='http://player.youku.com/embed/', verbose_name='youko url'),
            preserve_default=False,
        ),
    ]
