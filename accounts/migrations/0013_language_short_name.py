# Generated by Django 2.1.7 on 2020-03-30 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_user_account_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='short_name',
            field=models.CharField(default='en', max_length=200),
        ),
    ]
