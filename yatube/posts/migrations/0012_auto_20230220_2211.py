# Generated by Django 2.2.16 on 2023-02-20 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20230219_2153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(help_text='Комментарий к посту', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Пост'),
        ),
    ]
