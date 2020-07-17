# Generated by Django 2.1.7 on 2020-03-30 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0007_auto_20200330_0758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='message_zn_ch',
            new_name='message_zh_hans',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='title_zn_ch',
            new_name='title_zh_hans',
        ),
        migrations.RenameField(
            model_name='notificationtemplate',
            old_name='message_template_zn_ch',
            new_name='message_template_zh_hans',
        ),
        migrations.RenameField(
            model_name='notificationtemplate',
            old_name='title_template_zn_ch',
            new_name='title_template_zh_hans',
        ),
    ]
