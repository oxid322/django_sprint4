# Generated by Django 3.2.16 on 2024-11-10 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-pub_date'], name='blog_post_pub_dat_b2b442_idx'),
        ),
    ]
