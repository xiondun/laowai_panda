# Generated by Django 2.1.7 on 2020-03-06 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect', '0012_merge_20200210_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_chn',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_de',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_esp',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_fr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_in',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ind',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_it',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_jp',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_kp',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_kr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_my',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_pe',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_pt',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ru',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_th',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_tr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ur',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_vn',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
