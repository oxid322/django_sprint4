# Generated by Django 3.2.16 on 2024-11-10 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20241110_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.CharField(max_length=512),
        ),
    ]
